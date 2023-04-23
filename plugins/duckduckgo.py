from duckduckgo_search import ddg
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('query')
args = parser.parse_args()

print(ddg(args.query, max_results=6))
