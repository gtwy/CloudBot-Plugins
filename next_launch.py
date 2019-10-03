#   James' CloudBot Plugins      https://github.com/gtwy/CloudBot-Plugins
#
#   Responds to commands "nextlaunch" / "nl" with the next rocket launch.
#   Add a search term to search. E.g. "nl falcon 9"
#
#   Script will automatically broadcast if a launch is imminent
#
#   Requirements:
#      * launchlibrary API      https://pypi.org/project/python-launch-library/

from cloudbot import hook
from cloudbot.bot import bot
from datetime import datetime, timezone, timedelta
import launchlibrary as ll
import re
from sqlalchemy import Table, Column, String, Integer, Boolean
from cloudbot.util import database


# Sqlachemy tables and functions
table = Table('launchlibrary2',
      database.metadata,
      Column('launchid', Integer, primary_key=True),
      Column('netdate', Integer),
      Column('notifyt24', Boolean, default=False),
      Column('notifyt01', Boolean, default=False)
      )

async def add_entry(async_call, db, launchid, netdate):
   query = table.insert().values(
         launchid=launchid,
         netdate=netdate
         )
   await async_call(db.execute, query)
   await async_call(db.commit)

async def update_entry(async_call, db, launchid, netdate):
   query = table.update() \
         .where(table.c.launchid == launchid) \
         .values(netdate=netdate)
   await async_call(db.execute, query)
   await async_call(db.commit)

async def notify_entry24(async_call, db, launchid, switch=True):
   query = table.update() \
         .where(table.c.launchid == launchid) \
         .values(notifyt24=switch)
   await async_call(db.execute, query)
   await async_call(db.commit)

async def notify_entry01(async_call, db, launchid, switch=True):
   query = table.update() \
         .where(table.c.launchid == launchid) \
         .values(notifyt01=switch)
   await async_call(db.execute, query)
   await async_call(db.commit)

async def del_entries(async_call, db):
   cutoff = datetime.now(timezone.utc) - timedelta(hours=2)
   query = table.delete() \
         .where(table.c.netdate < int(cutoff.timestamp()))
   await async_call(db.execute, query)
   await async_call(db.commit)


# Initialize API
@hook.on_start()
async def ll_api():
   global llapi

   # Initialize Launch Library API
   llapi = ll.Api(retries=10)

# Load cache from sqlachemy
@hook.on_start()
async def load_cache(async_call, db):
   global ll_cache
   ll_cache = []
   for launchid, netdate, notifyt24, notifyt01 in (await async_call(_load_cache_db, db)):
      ll_cache.append((launchid, netdate, notifyt24, notifyt01))

def _load_cache_db(db):
    query = db.execute(table.select())
    return [(row['launchid'], row['netdate'], row['notifyt24'], row['notifyt01']) for row in query]

# Function to download list of launches
def getLaunches(lchsearch=''):
   # Download list of search results.
   try:
      if not lchsearch: # No search term entered, just pull the next launch
         lchlist = ll.Launch.fetch(llapi, next=25)
      else: # Search term entered. Download list of next 300 launches and then filter with search term
         lchlist = list(filter(lambda x: lchsearch.lower() in x.name.lower(), ll.Launch.fetch(llapi, next=300)))
   except Exception:
      print ('Something went wrong, either you entered an invalid search string or the API is down.')
      lchlist = []
      raise
   return lchlist;

# Function to build the output string
def launchOut(lch):
   # Name - Location. E.g.    'H-IIB 304 | Kounotori 8 (HTV-8) - Osaki Y LP2, Tanegashima, Japan - '
   lchout = lch.name + ' - ' + lch.location.pads[0].name + ' - '

   # If a video feed exists, append to output
   if len(lch.vid_urls) > 0:
      lchout  += re.sub(r'(www\.){0,1}youtube\.com\/watch\?v=', 'youtu.be/', lch.vid_urls[0], flags=re.IGNORECASE) + ' - '

   # TBD or just NET. NET = No Earlier Than. If not TBD, put the countdown.
   if lch.tbddate==1 or lch.tbdtime==1:
      lchout += 'TBD/NET ' + str(lch.net)
   else:
      countd = lch.net - datetime.now(timezone.utc)
      days, countr = divmod(int(countd.total_seconds()), 86400)
      hours, countr = divmod(countr, 3600)
      minutes, seconds = divmod(countr, 60)
      countout = ''
      if int(days) > 0:
         countout += ('{} day'.format(days))
         if int(days) > 1:
            countout += 's'
         countout += ' '
      final = '{}{:02}:{:02}:{:02}'.format(countout, int(hours), int(minutes), int(seconds))
      lchout += 'NET ' + lch.net.strftime('%Y-%m-%d %H:%M:%S %Z') + ' (T-' + final + ')'

   return lchout;

# Function to make sure there were were results
def launchCheck(lchlist, lchsearch=''):
   if len(lchlist) > 0:
      lchout = launchOut(lchlist[0])
   else:
      if not lchsearch:
         lchout = 'Something went wrong. Maybe the Launch Library API is down?'
      else:
         lchout = 'No future launches found matching search term: ' + lchsearch

   return lchout;

# Function to send messages to the channel
def sendLaunch(bot, async_call, db, lchout):
   network = bot.config.get('james-plugins', {}).get('launch_output_server', None)
   if not network:
      network = 'freenode'
   channel = bot.config.get('james-plugins', {}).get('launch_output_channel', None)
   if not channel:
      channel = '#lowtech-dev'
   if network in bot.connections:
      conn = bot.connections[network]
      if conn.ready:
         out = ''
         conn.message(channel, lchout)

# Watch for future launches and send to channel
@hook.periodic(60 * 5)
async def launchlibrarybot(bot, async_call, db):

   # Delete old launches
   await del_entries(async_call, db)
   await load_cache(async_call, db)

   # Compares launch library with local database and acts accordingly
   lchlist = getLaunches()
   if len(lchlist) > 0:
      for lch in lchlist:
         exists = False
         datesame = False
         didnotify24 = False
         didnotify01 = False
         lchtime = int(lch.net.timestamp())
         for result in ll_cache:
            cacheid, cachedate, notifyt24, notifyt01 = result

            # Get applicable record and pass variables
            if lch.id == cacheid:
               exists = True
               if lchtime == cachedate:
                  datesame = True
               didnotify24 = notifyt24
               didnotify01 = notifyt01

         if not exists: # Add new entry to database
            await add_entry(async_call, db, lch.id, lchtime)
            await load_cache(async_call, db)

         if exists and not datesame: # NET date changed. Update database
            await update_entry(async_call, db, lch.id, lchtime)
            await load_cache(async_call, db)

            # Send message to the channel that the date has changed
            sendLaunch(bot, async_call, db, launchOut(lch))

            # New date is more than 30 hours away, reset T-24 hr notification
            if lch.net > (datetime.now(timezone.utc) + (timedelta(hours=30))):
               await notify_entry24(async_call, db, lch.id, False)
               await load_cache(async_call, db)

            # Reset T-1 hr clock regardless
            await notify_entry01(async_call, db, lch.id, False)
            await load_cache(async_call, db)

         if not didnotify24 and lch.net < (datetime.now(timezone.utc) + timedelta(hours=24)):  # Less than T-24 hrs until launch
            await notify_entry24(async_call, db, lch.id)
            await load_cache(async_call, db)

            # Send a message to the channel that T-24 hrs til launch
            sendLaunch(bot, async_call, db, launchOut(lch))

         if not didnotify01 and lch.net < (datetime.now(timezone.utc) + timedelta(hours=1)):   # Less than T-1 hr until launch
            await notify_entry01(async_call, db, lch.id)
            await load_cache(async_call, db)

            # Send a message to the channel that T-1 hr til launch
            sendLaunch(bot, async_call, db, launchOut(lch))

# Respond to manual queries with the "nl" or "nextlaunch" command
@hook.command('nextlaunch', 'nl')
async def nextlaunch(text, message):
   lchsearch = text.strip()

   # Get launches
   lchlist = getLaunches(lchsearch)

   # Are there any results?
   msg = launchCheck(lchlist, lchsearch)

   # Output
   message(msg)
