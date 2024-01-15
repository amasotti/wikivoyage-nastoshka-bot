import argparse
from runner import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run the wikivoyage Nastoshka bot',
        usage='main.py -s <script> [-l <lang> -t <total>]\navailable scripts:\n' +
              '\tcitylist-checker : Check the citylist for wikidata ids'
    )
    parser.add_argument('-s', '--script', help='Run a specific script', required=False)
    parser.add_argument('-l', '--lang', help='The language to use', required=False, default='it')
    parser.add_argument('-t', '--total', help='The total number of articles to check', required=False, default=1)
    parser.add_argument('--target-page', help='The target page for the script', required=False, default=None)
    parser.add_argument('--target-template', help='The name of the template to sort', required=False, default=None)
    args = parser.parse_args()
    run(args)
