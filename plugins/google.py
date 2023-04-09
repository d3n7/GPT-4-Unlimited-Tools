from googlesearch import search
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('query')
args = parser.parse_args()

for i in search(args.query, advanced=True, num_results=6):
    print(i)
