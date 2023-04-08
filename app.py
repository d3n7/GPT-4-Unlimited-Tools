import re, subprocess, openai, random
import pandas as pd
import numpy as np
import streamlit as st
from streamlit_chat import message

# some helper vars and functions
if 'displayChat' not in st.session_state:
    st.session_state['displayChat'] = False
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'running' not in st.session_state:
    st.session_state['running'] = False
regx = [r'[A-Z]+\((?:[^()]*|\([^()]*\))*\)', r'''(?:"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\b[^,]+)'''] #parsing commands, parsing arguments
sysPrompt = 'You now have access to some commands to help complete the user\'s request. You are able to access the user\'s machine with these commands. In every message you send, include "COMMAND: " with your command at the end. Here is a list of commands with explanations of how they are used:\n{}\n When you use a command, the user will respond with "Response: " followed by the output of the commmand. Use this output to help the user complete their request.'

def formatTable(table):
    lines = ''
    for x, i in enumerate(table['GPT Commands']):
        lines += '{} - {}\n'.format(table['GPT Commands'][x],table['GPT Explanations'][x])
    return(lines)

# WEB APP
st.markdown('# GPT-4 + CUSTOM PLUGINS')
st.markdown('Made by [d3nt](https://github.com/d3n7) to give GPT-4 access to any commands/scripts you want via the command line. This unlocks the ability for GPT-4 to interact with the internet, APIs, and any applications that you could with a CLI. Basically it\'s open source, flexible, plugins for GPT-4.')

#User inputs
st.markdown('### OpenAI Settings')
openaikey = st.text_input('OpenAI API Key', type='password')
modelV = st.selectbox('Model', ('GPT-4', 'GPT-3.5-Turbo'))
st.markdown('### Editable Knowledge Base\nDelete any commands will not need to save tokens and increase accuracy.\n\nBe careful with the Raw Translation column. This is code that gets executed by your machine.')
d = {'GPT Commands': ['GOOGLE("question")', 'PYTHON(script.py)', 'MAKEFILE("content\\nhere", filename.txt)', 'READFILE(filename.txt)', 'LISTFILES()'],
     'GPT Explanations': ['Search Google with the given text and return the results', 'Run a python script with the given file name. Do not use quotes for the filename argument.', 'Make a file with the given content and file name.', 'Read the content of a given filename', 'List the files you have access to'],
     'Raw Translation': ['python plugins/google.py {}', 'python files/{}', 'echo {} > files/{}', 'cat files/{}', 'ls files']
     }
df = pd.DataFrame(data=d, dtype='string')
commandTable = st.experimental_data_editor(df, use_container_width=True, num_rows='dynamic')
st.markdown('### Chat')
prompt = st.text_input('Message')
col1, col2, col3 = st.columns(3)
with col2:
    newSession = st.checkbox('New Session', True)
with col3:
    showAll = st.checkbox('Show Commands And Outputs', False)

#Send to GPT
with col1:
    if st.button('Send'):
        st.session_state['running'] = True

def askGPT(input):
    st.session_state['history'].append({'role': 'user', 'content': input})
    with st.spinner('Talking to OpenAI...'):
        r = openai.ChatCompletion.create(model=modelV.lower(), messages=st.session_state['history'])
    resp = r['choices'][0]['message']['content']
    st.session_state['history'].append({'role': 'assistant', 'content': resp})
    return resp

if st.session_state['running']:
    st.session_state['running'] = False
    if prompt != '' and openaikey != '':
        if newSession or st.session_state['history'] == []:
            st.session_state['history'] = [{'role': 'system', 'content': sysPrompt.format(formatTable(commandTable))}]

        if not st.session_state['displayChat']:
            st.session_state['displayChat'] = True

        openai.api_key = openaikey
        response = askGPT(prompt)

        #parse GPT commands, possible back and forth
        while len(re.findall(regx[0], response)) >= 1:
            userResponses = []
            for cmd in re.findall(regx[0], response):
                stem = ''
                rawArgs = ''
                cmdId = -1
                fPrompt = ''
                for x, i in enumerate(cmd):
                    if i == '(':
                        stem = cmd[:x]
                        rawArgs = cmd[x+1:][:-1]
                        break
                rawArgs.replace('\n','\\n')
                rawArgs.replace('\\\n', '\\n')
                for x, i in enumerate(commandTable['GPT Commands']):
                    if stem in i:
                        cmdId = x
                        break

                if cmdId == -1:
                    fPrompt = 'Response: Unrecognized command'
                elif '\'\'\'' in rawArgs:
                    fPrompt = 'Response: Error parsing multi-line string (\'\'\') Use double quotes and escaped newlines instead (")'
                else:
                    command = commandTable['Raw Translation'][cmdId]
                    args = []
                    if rawArgs != '':
                        args = re.findall(regx[1], rawArgs)
                        command = command.format(*args)
                    singleQuotes = False
                    for i in args:
                        if i.startswith("'"):
                            singleQuotes = True
                            fPrompt = "Response: Error parsing argument in single quotes. Use double quotes instead"
                            break
                    if not singleQuotes:
                        with st.spinner('Running command \''+command+'\''):
                            try:
                                p = subprocess.Popen(command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
                                fPrompt = 'Response: '+p.communicate()[0].decode("utf-8")
                            except subprocess.CalledProcessError as e:
                                fPrompt = 'Response: '+e.output.decode("utf-8")
                userResponses.append(fPrompt)

            response = askGPT('\n'.join(userResponses))

    else:
        st.warning('Make sure OpenAI key and prompt entered', icon='⚠️')

if st.session_state['displayChat']:
    for i in st.session_state['history']:
        if i['role'] == 'user':
            if not showAll:
                if 'Response:' not in i['content']:
                    message(i['content'], is_user=True)
            else:
                message(i['content'], is_user=True)
        elif i['role'] == 'assistant':
            if not showAll:
                if 'COMMAND' not in i['content']:
                    message(i['content'])
            else:
                message(i['content'])
