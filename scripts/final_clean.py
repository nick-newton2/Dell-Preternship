#!/usr/bin/env python3

import csv
import json
import sys
import os
import json
import string

# Function to convert a CSV to JSON
def read_json(jsonFilePath):
    # JSON file
    f = open (jsonFilePath, "r")
    # Reading from file
    data = json.loads(f.read())
    # Closing file
    f.close()
    return data

def convert(timezone): #returns a time difference when a string timezone response from the form is passed in
    if timezone == "EST":
        return 0
    elif timezone == "South America East":
        return 1
    elif timezone == "Iceland":
        return 4
    elif timezone == "Europe London":
        return 5
    elif timezone == "Europe Munich":
        return 6
    elif timezone == "Africa Egypt":
        return 7
    elif timezone == "Asia Kabul":
        return 8
    elif timezone == "Asia Maldives":
        return 9
    elif timezone == "Asia Dhaka":
        return 10
    elif timezone == "Asia Phnom Penh":
        return 11
    elif timezone == "Asia Kuala Lumpurt":
        return 12
    elif timezone == "Asia Tokyo":
        return 13
    elif timezone == "Asia Melbourne":
        return 14
    elif timezone == "Pacific Guadalcanal":
        return 15
    elif timezone == "Pacific Fiji":
        return 16
    elif timezone == "Pacific Honolulu":
        return 18
    elif timezone == "US Los Angeles":
        return 21
    elif timezone == "US Denver":
        return 22
    elif timezone == "US Chicago":
        return 23

def get_weight(pos): #returns the position weight of the member from the form/json response
    if pos == "Presenter":
            return 5
    elif pos == "President":
            return 4
    elif pos =="VP/Executive":
            return 3
    elif pos=="Manager":
            return 2
    elif pos=="Employee":
            return 1
    else:
            return 0

def add_arr(meeting, mask, weight, over, ride): #creates the meeting array

    if over==0: #normal case
        for i in range(1, 25):
            if( mask&(1<<(24-i)) ):
                meeting[i] += weight
    elif over==1: #override case
        for i in range(1, 25):
            if( mask&(1<<(24-i)) ):
                if(ride&1<<(24-i)): #additional case to test for override
                    meeting[i] += weight
    return meeting

def create_list(data, i): #converts string available times into a integer list
    count = len(data)
    x=[]
    p=data[str(i)]["Time"]
    string= ""

    for i in range (0,len(p)):
        if p[i] != "," and p[i]!= " ":
            string =string + p[i]
        elif p[i] == ",":
            x.append(int(string))
            string=""

    return (x)

def create_bits(x): #creates bitmask
    mask= 000000000000000000000000

    for i in range(0,len(x)):
        mask= mask | 1<<(24-x[i])
    return mask

def get_over(data, name):
    ride=0
    p=data[str(name)]["Time"]
    string= p[0]
    x=create_list(data, name)

    #convert times to standard
    timezone= data[str(name)]["Zone"]
    standard=convert(timezone)
    for j in range(0, len(x)):
        if x[j]+standard<= 24:
            x[j]= x[j]+standard
        else:
            x[j]= x[j]+standard-24

    #get bitmask
    ride=create_bits(x)
    return ride

def get_list(data, name, over): #gets the meeting and impacted timezones
    count = len(data)
    x=[]
    mask=0
    y=1
    meeting=[0]*25 #initialize meeting array size for 24 hours, ignoring index 0
    zone= set()
    ride=0

    if over==1: #here seeing if we need to find and save the override bitset for later
        ride=get_over(data, name)

    for i in range(1,count+1):
        p=data[str(i)]["Time"]
        string= p[0]
        x=create_list(data, i) #person local availability list

        #convert times to standard
        timezone= data[str(i)]["Zone"]
        zone.add(timezone) #append timezone set
        standard=convert(timezone)
        for i in range(0, len(x)): #timezone conversion
            x[i] = (x[i] + standard) % 24


        #get bitmask
        mask=create_bits(x)

        #get weight
        pos= data[str(y)]["Position"]
        y += 1
        weight=get_weight(pos)

        #compare and append array from mask
        meeting=add_arr(meeting, mask, weight, over, ride)

    return meeting, zone

def check_override(data, count): #see if there is a member who must be at the meeting, over is a bool, name is the location of the person in the json
    for i in range(1, count+1):
        override=data[str(i)]["Override"]
        if override == "Yes":
            over=1
            name=i
            break
        else:
            over=0
            name=1
    return over, name

def display(meeting, zones, people, data, over, name): #display
    m = []
    percentages = []
    m, percentages = find_times(meeting, people)

    if m[0] == 0:
        print("No potential meeting times")
    else:
        print("\nMeeting times:\n")
        if over==1:
            print(f'Times for {data[str(name)]["Name (first)"]}:\n')

        print("Percentage of people available (weighted)")
        print(" " * 16, end="")

        for percent in percentages:
            print(f"{percent:9.2}\t", end= "")

        print("")

        for zone in zones:              #range(0, len(zone)):
            print(zone)                #zone[i])
            diff = convert(zone)       #zone[i])
            n = []
            n = normal_time(diff, m)
            print("Times: \t\t", end="")
            for i in range(len(n)):
                print(f"{i + 1}. {n[i]:>3}:00\t", end = "")
            print("")

def normal_time(diff, m):
    n = []
    for i in m:
        if i != 0:
            n.append((i + diff) % 24)
    return n

def find_times(meeting, people): #finds top 3 times, sees if these fit in thr bounds of an acceptable time based on attendance
    temp1 = 0
    temp2 = 0
    m = [0,0,0] # indices of the optimal timezones in order
    N = .5

    for i in range(1, 25):
        val = meeting[i]
        #print(val, m) #--> to show that the array is def max
        if val > meeting[m[0]]:
            temp1 = m[0]
            temp2 = m[1]
            m[0] = i
            m[1] = temp1
            m[2] = temp2
        elif val > meeting[m[1]]:
            temp2 = m[1]
            m[1] = i
            m[2] = temp2
        elif val > meeting[m[2]]:
            m[2] = i

    percentages = []
    for i in range(len(m)):
        percentage = meeting[m[i]]/people
        if percentage < N:
            m[i] = 0
        else:
            percentages.append(percentage)

    return m, percentages


def get_people_weight(data): #gets the number of members invited that filled out the form
    people = 0
    for i in range(len(data)):
        people += get_weight(data[str(i + 1)]['Position'])

    return people


def main():
    arg = str(sys.argv[1])
    jsonFilePath = arg
    data=read_json(jsonFilePath)
    count=len(data)
    over, name= check_override(data, count)
    meeting, zones=get_list(data, name, over)
    people=get_people_weight(data)

    display(meeting, zones, people, data, over, name)


# Main Execution
if __name__ == '__main__':
    main()

