import replicate
import argparse, os

#enter your api token for replicate
apiToken = '<API KEY>'

filesPath = os.path.realpath(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir), 'files'))
parser = argparse.ArgumentParser()
parser.add_argument('question')
parser.add_argument('img')
args = parser.parse_args()

if apiToken != '<API KEY>':
    os.environ['REPLICATE_API_TOKEN'] = apiToken
    output = replicate.run(
        'andreasjansson/blip-2:4b32258c42e9efd4288bb9910bc532a69727f9acd26aa08e175713a0a857a608',
        input={'image': open(os.path.join(filesPath,args.img), 'rb'), 'question': args.question}
    )
    print(output)
else:
    print('Error: Tell the user to add their Replicate API token to plugins/blip2.py')