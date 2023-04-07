from googlesearch import search
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('url')
args = parser.parse_args()

for i in search(args.url, advanced=True, num_results=6):
    print(i)