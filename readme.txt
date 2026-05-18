The purpose of this github project is
1. to read match plan for a certain club from website fussball.de
2. to convert the match data into a iCal calendar file
3. to automate the match data reading with and iCal generation with github
4. to provide the iCal file to the public to be ready to be imported into an online calendar (e.g. google calendar)

This is done with a python script to convert data from fussball.de to iCal file
and with github to update this every 6 hours and to provide the iCal file via github link

The python script is adapted for a very special application:
Club: Sportfreunde Großsachsenheim
Consideration of matches in the home location only
Consideration of matches for a specific football field only
The intension is to get an overview when the specific football field is used for matches
and to control the field maintenance (gras-robot)
