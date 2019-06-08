"# HearthScryParser" 

HearthScry parser is a json to csv parser for the HearthScry Track-O-Bot created to provide a easy to use parsing script.
For more information on the data (and public Data) and Track-O-Bot go to <a href="http://www.hearthscry.com/">http://www.hearthscry.com/</a>.

"#Using HearthScry Parser"

This a Python Script

python hearthscryparser -t 20 "2019-06-01.json" -o "New_File_"

will process your "2019-06-01.json" file and Create "New_File_Atribute_Log.csv" and  "New_File_Event_Log.csv"

-t 20 consider that every turn will take 20 seconds, is used so event logs have a readable starting time for Process Mining.

Reading ini file:

{

  "Classes_POV" : ["*"],   # use ["*"] to the add all classes, it's possible to use ["Hunter","Mage"] to add only this two classes
  
  "Classes_Opponent" : ["*"], # use this to limit opponent classes use the same principle as Previous option
    
  "excluded_class_POV" : ["Warlock"], # use this to remove a class from parsing, easier than adding one by one in fist attribute
  
  "excluded_class_Opponent" : none, # same as Previous, use none or [""] to do not remove any
  
  "game_mode" : ["ranked"], # use this to limit the game mode, is a list of game modes
  
  "attributes" : ["unique_id","region","start_time","mode","rank","pov_class","opponent_class","pov_is_first","max_turns","result"],
  
  "count_cards" : [
    {"name" :  "Flanking Strike"},
    {"id" :  "CFM_120"}
  ], #Count card is a built in method to count played card, simply add { "name" : "<card name>" } or { "id" : "<card id>"} and the the parser will count the number that this card is played
  
  "export_event_log" : "True", # Export the Event log of played cards, disabling this Do not improve efficiency
  
  "remove_tainted" : "True" # Some games are considered Tainted and you might want to remove them from your list
  
}