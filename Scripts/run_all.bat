echo "Running Python Scripts Necessary for Thesis" 
echo "building dicts"
Python.exe build_dicts.py
Python.exe build_wireless_dicts.py

echo "building fed dicts"
Python.exe Build_FED_dict.py

echo "plotting br compare"
Python.exe bedroom_compare.py

echo "victim stats"
Python.exe victim_stats.py

echo "temperature repeatability"
Python.exe temperature_repeatability.py

echo "repeatability"
Python.exe repeatability.py

