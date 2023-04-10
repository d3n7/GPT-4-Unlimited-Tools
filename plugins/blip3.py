import replicate
import argparse, os

#alternate version for huggingface

filesPath = os.path.realpath(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir), 'files'))
parser = argparse.ArgumentParser()
parser.add_argument('question')
parser.add_argument('img')
args = parser.parse_args()

if os.environ['REPLICATE_API_TOKEN'] != '':
    output = replicate.run(
        'andreasjansson/blip-2:4b32258c42e9efd4288bb9910bc532a69727f9acd26aa08e175713a0a857a608',
        input={'image': open(os.path.join(filesPath,args.img), 'rb'), 'question': args.question}
    )
    print(output)
else:
    print('Error: Tell the user to add their Replicate API token to the above settings section')
