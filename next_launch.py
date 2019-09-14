from datetime import datetime, timezone
import launchlibrary as ll
import re

@hook.on_start()
async def ll_api():
   global llapi

   # Initialize Launch Library API
   api = ll.Api(retries=10)


@hook.command('nextlaunch', 'name', singlethread=True)
def nextlaunch(text='', reply):
   """<string> - Prints next launch matching string"""
   lchsearch = text.strip()
   try:
      # Pull a list of search results. (If no search term was entered, pull the next launch.)
      if len(lchsearch) > 0:
         lchlist = list(filter(lambda x: lchsearch.lower() in x.name.lower(), ll.Launch.fetch(api, next=300)))
      else:
         lchlist = ll.Launch.fetch(api, next=1)
   except Exception:
      reply("Something went wrong, either you entered an invalid search string or the API is down.")
      raise
   # First result
   lch = lchlist[0]

   # Name - Location. E.g.    'H-IIB 304 | Kounotori 8 (HTV-8) - Osaki Y LP2, Tanegashima, Japan - '
   lchout = lch.name + ' - ' + lch.location.pads[0].name + ' - '

   # If a video feed exists, append to output
   if len(lch.vid_urls) > 0:
      lchout  += re.sub(r'(www\.){0,1}youtube\.com\/watch\?v=', 'youtu.be/', lch.vid_urls[0], flags=re.IGNORECASE) + ' - '

   # TBD or just NET. NET = No Earlier Than. If not TBD, put the countdown.
   if lch.tbddate==1 or lch.tbdtime==1:
      lchout += 'TBD/NET ' + str(lch.net)
   else:
      lchout += 'NET ' + str(nl.net) + ' - T-' + str(nl.net - datetime.now(timezone.utc))
   return lchout
