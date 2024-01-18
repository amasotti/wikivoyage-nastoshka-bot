# This is an automatically generated file. You can find more
# configuration parameters in 'config.py' file or refer
# https://doc.wikimedia.org/pywikibot/master/api_ref/pywikibot.config.html
from typing import Optional, Union
from pywikibot.backports import List

family = 'wikivoyage'
mylang = 'it'
usernames['wikivoyage']['it'] = "YOUR_USERNAME"
password_file = "user-password.py"
log: List[str] = []
logfilename: Optional[str] = None
# maximal size of a logfile in kilobytes. If the size reached that limit the
# logfile will be renamed (if logfilecount is not 0) and the old file is filled
# again. logfilesize must be an integer value
logfilesize = 1024
# Number of rotating logfiles are created. The older files get the higher
# number. If logfilecount is 0, no logfile will be archived but the current
# logfile will be overwritten if the file size reached the logfilesize above.
# If logfilecount is -1 there are no rotating logfiles but the files where
# renamed if the logfile is full. The newest file gets the highest number until
# some logfiles where deleted.
logfilecount = 5
# set to 1 (or higher) to generate "informative" messages to terminal
verbose_output = 0
# set to True to fetch the pywiki version online
log_pywiki_repo_version = False
# if True, include a lot of debugging info in logfile
# (overrides log setting above)
debug_log: List[str] = []

# ############# EXTERNAL SCRIPT PATH SETTINGS ##############
# Set your own script path to lookup for your script files.
#
# Your private script path is relative to your base directory.
# Subfolders must be delimited by '.'. every folder must contain
# an (empty) __init__.py file.
#
# The search order is
# 1. user_script_paths in the given order
# 2. scripts/userscripts
# 3. scripts
# 4. scripts/maintenance
# 5. pywikibot/scripts
#
# 2. - 4. are available in directory mode only
#
# sample:
# user_script_paths = ['scripts.myscripts']
user_script_paths: List[str] = ["bot/wikivoyage/scripts", "bot/wikidata/scripts"]

