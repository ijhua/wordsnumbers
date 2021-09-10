import random

def weighted_pick(dic):
    r = random.uniform(0, sum(dic.values()))
    s = 0.0
    for k, w in dic.items():
        s += w
        if r < s: return k
    return k

def letter_classifier(st):
    vowel_count = 0
    consonant_count = 0
    for i in st:
        if i in 'aeiou':
            vowel_count += 1
        elif i in 'bcdfghjklmnpqrstvwxyz':
            consonant_count += 1
    return vowel_count,consonant_count

def letter_adder(dic):
    letter = weighted_pick(dic)
    dic[letter] -=1
    return letter

import pandas as pd

df = pd.read_excel("Words.xlsx", engine='openpyxl')

def word_check(st):
    #convert string to set in order to match alphagram
    st = st.upper()
    word = "".join(sorted(st))
    ref = df[["Alphagram","Word(s)"]]
    #does the alphagram match?
    alpha_match = (ref["Alphagram"]==word).any()
    if alpha_match:
        #sometimes there are multiple words that match the alphagram, so need to make sure that the word was spelled correctly
        ref_word = ref[(ref["Alphagram"]==word)]["Word(s)"].values[0]
        if "/" in ref_word:
            ref_words = ref_word.split("/")
            if st in ref_words:
                #print(st + " is an acceptable word.")
                return True
            else:
                #print(st + " is not an acceptable word.")
                return False
        elif st == ref_word:
            #print(st + " is an acceptable word.")
            return True
        else:
            #print(st + " is not an acceptable word.")
            return False
    else:
        #print(st + " is not an acceptable word.")
        return False
def letter_check(st,letter_list):
    #need to check that the user input string uses only letters from the letter list and doesn't go over the limit
    #can't use sets because repeated letters are OK
    if len(st) > 9:
        #print("Too many letters in "+ st)
        return False
    word_list = list(st)
    temp_letters = list(letter_list) #had to do this step or else the letter list got overwritten
    while (len(word_list))>0:
        if word_list[0] in temp_letters:
            temp_letters.remove(word_list[0])
            word_list.remove(word_list[0])
        else:
            #print("Word is not valid. "+word_list[0].upper() +" is not in the list of acceptable letters")
            return False
            break
    if len(word_list)==0:
        return True
    else:
        #print(st + "does not use the correct letters")
        return False
    
def nonvalid_word(st,letter_list):
    if len(st) > 9:
        response = "Too many letters in "+ st
        return response
    word_list = list(st)
    temp_letters = list(letter_list) #had to do this step or else the letter list got overwritten
    while (len(word_list))>0:
        if word_list[0] in temp_letters:
            temp_letters.remove(word_list[0])
            word_list.remove(word_list[0])
        else:
            response = word_list[0].upper() +" is not in the list of acceptable letters"
            return response
            break
    if len(word_list)!=0:
        response = (st + "does not use the correct letters")
        return response

word_key = list(df["Single Word"].dropna())

def best_word(letter_list):
    matches = []
    for w in word_key:
        word_alpha = sorted(list(w))
        alpha = sorted([x.upper() for x in letter_list])
        while len(word_alpha) > 0:
            if word_alpha[0] in alpha:
                alpha.remove(word_alpha[0])
                word_alpha.remove(word_alpha[0])
            else:
                break
        if len(word_alpha) == 0:
            matches.append(w)
        else:
            continue
    best_df = df[df["Single Word"].isin(matches)]
    best_length = best_df["Length"].max()
    best = best_df[best_df["Length"]==best_length].sort_values(by="Weighted Usefulness Score",ascending=False)["Single Word"].reset_index(drop=True)[0]
    return matches,best

from config import *
import requests
import json

def oxford_lookup(word):
    language = 'en-gb'
    word_id = word.lower()
    url = 'https://od-api.oxforddictionaries.com/api/v2/entries/'  + language + '/'  + word+"?fields=definitions&strictMatch=false"
    r = requests.get(url, headers = {'app_id' : app_id, 'app_key' : app_key})
    defs = []
    if r.status_code == 200:
        for i in r.json()["results"][0]["lexicalEntries"][0]["entries"][0]["senses"]:
            defs.append(i["definitions"][0].capitalize())
    else:
        defs.append("Definition not found. I don't want to pay for more features")
    return defs

from tkinter import *
from tkinter import ttk

def pick_vowels():
    global vowels
    global x
    global directions
    if len(x.get())<9:
        num_vowels = letter_classifier(x.get().lower())[0]
        if num_vowels < 5:
            let = letter_adder(vowels).upper()
            x.set(x.get()+let)
        else:
            directions.set(directions.get()+"\nMax vowels already reached!")
    else:
        directions.set(directions.get()+"\nMax letters reached!")
        

def pick_consonants():
    global consonants
    global x
    global directions
    num_consonants = letter_classifier(x.get().lower())[1]
    if len(x.get())<9:
        if num_consonants < 6:
            let = letter_adder(consonants).upper()
            x.set(x.get()+let)
        else:
            directions.set(directions.get()+"\nMax consonants already reached!")
    else:
        directions.set(directions.get()+"\nMax letters reached!")
        
def eval_word():
    global x
    global word
    global result
    letters = list(x.get().lower())
    if letter_check(word.get().lower(),letters) and word_check(word.get().lower()):
        result.set(result.get()+"\n"+word.get().upper()+" ("+str(len(word.get()))+") "+" is acceptable")
    else:
        result.set(result.get()+"Word is not valid. "+str(nonvalid_word(word.get().lower(),letters)))
    possible, bestword = best_word(letters)
    possible_str = ", ".join(possible)
    result.set(result.get()+"\nPossible words were: "+possible_str+"\nThe best word was: "+ bestword +" ("+str(len(bestword))+")")
    definition = oxford_lookup(bestword)
    if definition is None:
        result.set(result.get()+"\nDefinition not found")
    else:
        word_def = str(definition)
        result.set(result.get()+"\n"+word_def)
        
def reset():
    global default_directions
    global default_x
    global default_word
    global default_result
    global directions
    global x
    global word
    global result
    directions.set(default_directions)
    x.set(default_x)
    word.set(default_word)
    result.set(default_result)
    
    
root = Tk()
root.title("Letters Game")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

vowels = {"a":15,"e":21,"i":13,"o":13,"u":5}
consonants = {"b":2,"c":3,"d":6,"f":2,"g":3,"h":2,"j":1,"k":1,"l":5,"m":4,"n":8,"p":4,"q":1,"r":9,"s":9,"t":9,"v":1,"w":1,"x":1,"y":1,"z":1}

#default strings
default_directions = "Welcome to the Letter Game!"+"\nChoose 9 letters using the vowel and consonant buttons and form the longest word possible."+" Evaluate the word when time runs out (to be implemented)."
default_x = ""


directions = StringVar(value=default_directions)
x = StringVar()
    
ttk.Label(mainframe, text=directions.get(), textvariable = directions,wraplength=500).grid(row=0, column=0,columnspan=6)
ttk.Label(mainframe, text=x.get(), textvariable = x).grid(row=1, column=1,columnspan=2)
ttk.Button(mainframe, text='Vowel', command=pick_vowels).grid(row=2, column=1)
ttk.Button(mainframe, text='Consonant', command=pick_consonants).grid(row=2, column=2)

ttk.Label(mainframe,text="Enter your word here:").grid(row=3,column=0)

default_word = ""
word = StringVar()
word_entry = ttk.Entry(mainframe, textvariable=word)
word_entry.grid(row=3,column=1,columnspan=2)

default_result = ""

ttk.Button(mainframe,text="Evaluate!",command=eval_word).grid(row=3,column=3)

ttk.Button(mainframe,text="Reset",command=reset).grid(row=4,column=3)

result = StringVar()
ttk.Label(mainframe, text=result.get(),textvariable=result,wraplength=500).grid(row=5,column=0,columnspan=6)

for child in mainframe.winfo_children(): 
    child.grid_configure(padx=5, pady=5)
    
root.mainloop()