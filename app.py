import re, subprocess, openai, random, regex
import pandas as pd
import numpy as np
import streamlit as st
from streamlit_chat import message

# some helper vars and functions
if 'displayChat' not in st.session_state:
    st.session_state['running'] = False  # Triggers main GPT loop
    st.session_state['followup'] = False # Follow flag for the main loop
    st.session_state['prompt'] = ''
    st.session_state['command'] = '' #command to be run locally
    st.session_state['acceptreject'] = False #shows accept/reject buttons for when commands are called
    st.session_state['history'] = [] #OpenAI convrsation history stored here
    st.session_state['displayChat'] = False
    st.session_state['displayCost'] = False
    st.session_state['totalCost'] = 0 # total cost of API calls
regx = [r"([A-Z]+\(((?:[^()\"']|(?:\"[^\"]*\")|(?:'[^']*')|\((?1)*\))*)\))",
        r'''(?:"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\b[^,]+)'''] #parsing commands, parsing arguments (thanks GPT-4)
#system message
sysPrompt = 'You now have access to some commands to help complete the user\'s request. ' \
            'You are able to access the user\'s machine with these commands. In every message you send, ' \
            'include "COMMAND: " with your command at the end. Here is a list of commands with ' \
            'explanations of how they are used:\n{}\n When you use a command, the user will respond ' \
            'with "Response: " followed by the output of the commmand. Use this output to help the ' \
            'user complete their request.'

#format command table for GPT-4
def formatTable(table):
    lines = ''
    for x, i in enumerate(table['GPT Commands']):
        lines += '{} - {}\n'.format(table['GPT Commands'][x],table['GPT Explanations'][x])
    return(lines)

#Ask GPT a prompt, update history and total cost, return a response
def askGPT(input, version):
    st.session_state['history'].append({'role': 'user', 'content': input})
    with st.spinner('Talking to OpenAI...'):
        r = openai.ChatCompletion.create(model=version, messages=st.session_state['history'])
    resp = r['choices'][0]['message']['content']
    costFactor = [0.03, 0.06] if version == 'gpt-4' else [0.002, 0.002]
    st.session_state['totalCost'] += r['usage']['prompt_tokens']/1000*costFactor[0]+r['usage']['completion_tokens']/1000*costFactor[1]
    st.session_state['history'].append({'role': 'assistant', 'content': resp})
    return resp

#restart main loop with followup flag
def followup():
    st.session_state['followup'], st.session_state['running'] = True, True
    st.experimental_rerun()

#run a GPT command or reject it
def runCmd(flag):
    if flag:
        with st.spinner('Running command \'' + st.session_state['command'] + '\''):
            try:
                p = subprocess.Popen(st.session_state['command'], shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
                p.wait()
                st.session_state['prompt'] = 'Response: ' + p.communicate()[0].decode("utf-8")
            except subprocess.CalledProcessError as e:
                st.session_state['prompt'] = 'Response: ' + e.output.decode("utf-8")
    else:
        st.session_state['prompt'] = "Response: User rejected this command"
    followup()

# WEB APP
st.markdown('# GPT-4 UNLIMITED PLUGINS')
st.markdown('Made by [d3nt](https://github.com/d3n7) to give GPT-4 access to any commands/scripts you want via the command line. This unlocks the ability for GPT-4 to interact with the internet, APIs, and any applications that you could with a CLI. Basically it\'s open source, flexible, plugins for GPT-4.')

#User inputs
st.markdown('### OpenAI Settings')
openaikey = st.text_input('OpenAI API Key', type='password')
modelV = st.selectbox('Model', ('GPT-4', 'GPT-3.5-Turbo'))

st.markdown('### Editable Knowledge Base\nDelete any commands will not need to save tokens and increase accuracy.\n\nBe careful with the Raw Translation column. This is code that gets executed by your machine.')
d = {'GPT Commands': ['GOOGLE("question")', 'PYTHON(script.py)', 'MAKEFILE("content\\nhere", filename.txt)', 'READFILE(filename.txt)', 'LISTFILES()', 'BLIP("What\'s in this image?", img1.jpg)'],
     'GPT Explanations': ['Search Google with the given text and return the results', 'Run a python script with the given file name. Do not use quotes for the filename argument.', 'Make a file with the given content and file name.', 'Read the content of a given filename', 'List the files you have access to', 'Ask BLIP-2, a vision model, a given question about a given image'],
     'Raw Translation': ['python plugins/google.py {}', 'cd files && python {} && cd ../', 'echo {} > files/{}', 'cat files/{}', 'ls files', 'python plugins/blip2.py {} {}']
     }
df = pd.DataFrame(data=d, dtype='string')
commandTable = st.experimental_data_editor(df, use_container_width=True, num_rows='dynamic')

st.markdown('### Chat')
prompt = st.text_input('Message')
col1, col2, col3, col4 = st.columns(4)
#this button triggers main loop
with col1:
    if st.button('Send'):
        st.session_state['running'] = True
with col2:
    newSession = st.checkbox('New Session', True)
with col3:
    showAll = st.checkbox('Show Commands And Outputs', False)
with col4:
    manualApproval = st.checkbox('Require Manual Approval', True)

#MAIN GPT LOOP
if st.session_state['running']:
    st.session_state['running'] = False #reset running flag

    #get user prompt
    if not st.session_state['followup']:
        st.session_state['prompt'] = prompt

    if openaikey != '':
        #set system prompt or update system prompt
        if (newSession or st.session_state['history'] == []) and (not st.session_state['followup']):
            st.session_state['history'] = [{'role': 'system', 'content': sysPrompt.format(formatTable(commandTable))}]
        else:
            st.session_state['history'][0] = {'role': 'system', 'content': sysPrompt.format(formatTable(commandTable))}
        st.session_state['followup'] = False #reset followup flag

        #turn on display for chat and cost if it's not already on
        if not st.session_state['displayChat']:
            st.session_state['displayChat'] = True
        if not st.session_state['displayCost']:
            st.session_state['displayCost'] = True

        #ask GPT-4
        openai.api_key = openaikey
        response = askGPT(st.session_state['prompt'], modelV.lower())

        #parse GPT commands, possibly trigger this loop again
        if len(regex.findall(regx[0], response)) >= 1:
            cmd = regex.findall(regx[0], response)[0][0]
            pIndex = cmd.index('(')
            stem = cmd[:pIndex]
            rawArgs = cmd[pIndex+1:][:-1]
            cmdId = -1

            #identify command
            for x, i in enumerate(commandTable['GPT Commands']):
                if stem in i:
                    cmdId = x
                    break

            #Handle incorrect command usage, or run the command
            rawArgs.replace('\n', '\\n')
            rawArgs.replace('\\\n', '\\n')
            if cmdId == -1:
                st.session_state['prompt'] = 'Response: Unrecognized command'
                followup()
            elif "'''" in rawArgs:
                st.session_state['prompt'] = 'Response: Error parsing multi-line string (\'\'\') Use a single line with escaped newlines instead (")'
                followup()
            elif '"""' in rawArgs:
                st.session_state['prompt'] = 'Response: Error parsing multi-line string (\"\"\") Use a single line with escaped newlines instead (")'
                followup()
            else:
                # Fetch command, turn raw argument string into a list of arguments, and format command
                st.session_state['command'] = commandTable['Raw Translation'][cmdId]
                args = []
                if rawArgs != '':
                    args = re.findall(regx[1], rawArgs)
                    st.session_state['command'] = st.session_state['command'].format(*args)

                # No single quote arguments allowed. Messes up MAKEFILE() and probably other commands.
                singleQuotes = False
                for i in args:
                    if i.startswith("'"):
                        singleQuotes = True
                        st.session_state['prompt'] = "Response: Error parsing argument in single quotes. Use double quotes around the argument instead"
                        followup()
                        break

                #If none of the above was a problem, run the command
                if not singleQuotes:
                    if manualApproval:
                        st.session_state['acceptreject'] = True
                    else:
                        runCmd(1)

    else:
        st.warning('Make sure OpenAI key is entered', icon='⚠️')

#UI for accepting/rejecting commands
col5, col6 = st.columns(2)
if st.session_state['acceptreject']:
    st.warning('GPT is trying to run the following command: ' + st.session_state['command'] + '\nPlease accept or reject this request.')
    with col5:
        if st.button('Accept'):
            st.session_state['acceptreject'] = False
            runCmd(1)
    with col6:
        if st.button('Reject'):
            st.session_state['acceptreject'] = False
            runCmd(0)

#display cost for the user
if st.session_state['displayCost']:
    st.info('Total OpenAI cost: $'+str(round(st.session_state['totalCost'],2)), icon='💸')

#display chat for the user
if st.session_state['displayChat']:
    for i in st.session_state['history']:
        if i['role'] == 'user':
            if not showAll:
                if 'Response:' not in i['content']:
                    message(i['content'], is_user=True, key=random.randint(1,9999))
            else:
                message(i['content'], is_user=True, key=random.randint(1,9999))
        elif i['role'] == 'assistant':
            if not showAll:
                if 'COMMAND' not in i['content']:
                    message(i['content'], key=random.randint(1,9999))
            else:
                message(i['content'], key=random.randint(1,9999))
