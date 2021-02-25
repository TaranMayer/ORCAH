# ORCAH Event Console Backend

This is the backend code for the ORCAH event console, and is a modified version of 18x18az's Clash in the Cloud event console software. 

## Changes I made to existing files:

 - echandler.py  
   - Updated if/else logic in the echandle function to account for the 5 additonal APIs I have added
 - ecdatabse.py
   - Added a pair of functions to insert/delete things from a table in ways that weren't permitted with the existing functions
   - Added functionality for a new table
 - eclib/apis.py
   - Added several new APIs for the new functionality of the event console regarding live matches
 - eclib/roles.py
   - Added access to abovementioned new APIs for the various roles
  
  
## Files I created from scratch:
  
- ecmodules/elims.py
  - Handles generating elimination matches based on qualification match results
- ecmodules/match_list.py
  - Handles updating the match list that appears on the `Matches` tab in the console
- ecmodules/rankings.py
  - Handles sorting teams into ranks based on WP, AP, and Skills score
- ecmodules/set_match.py
  - Handles updating the matches table in the database depending on what score is input by the referees
- eclib/db/matches.py
  - Sets up the `matches` table in the database



## 18x18az's original EC server code:

https://gitlab.com/18x18az/event-console/-/tree/server


   

