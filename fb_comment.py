# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 14:23:13 2022

@author: DIGHO D. T. Jordan
"""

import time
from facebook import GraphAPI
import fb_settings as settings

# Import question detection module
import question_analysis as QA

# Import comment classification module
import comment_analysis as CA


"""
===================================================================
"""

def verify_store_id(comments, admin):
    f = open(file='commented_id.txt', mode='r+')
    ids = f.readline().split(',')
    f.close()
    to_add = []
    needed= []
    
    for comment in comments:
        name_is = False
        try:
            name_is = comment['from']['name'] == admin
        except:
            pass
        if comment['id'] in ids or name_is:
            comments.remove(comment)
        else:
            to_add.append(comment['id'])
            needed.append(comment)
    
    # Add the no present ids in the ids file
    ids.extend(to_add)
    f = open(file='commented_id.txt', mode='w')
    f.write(','.join(ids))
    f.close()
    
    return needed


def reply_comments():
    try:
        # Get connexion to the Application in facebook with the token
        graph = GraphAPI(access_token=settings.ACCESS_TOKEN)
        
        # Get the User profil
        profil = graph.get_object(id=settings.PAGE_ID)
        
        # Get all the posts on the specified page
        posts = graph.get_connections(id=profil['id'], connection_name='posts')['data']
        #print(posts)
    except Exception as e:
        print('Could not connect to https://facebook.com !!!\nNetwork problems')
        return -1
    
    print('Connected to the page : ', profil['name'])
    
    for post in posts:
        """
        print('=====================================================')
        print('\tPost of ID : #', post['id'])
        print('=====================================================')
        """
        # Extract all the comments related to this post
        comments = graph.get_connections(id=post['id'], connection_name='comments')['data']
        
        # Get the untreated comments for treatment now
        comments = verify_store_id(comments=comments, admin=profil['name'])
        
        """
            Here we are going to integrate the code for classifying the comments
        """
        print('*** Post ID : ', post['id'].split('_')[1])
        if len(comments) == 0:
            print('No comment detected !!!\n')
        else:
            for comment in comments:
                # Check is we have a question
                if QA.is_a_question(comment['message']):
                    #graph.put_object(comment['id'], 'likes')
                    graph.put_comment(comment['id'], message='Question Detected.')
                    print('I am answering a question.\n')
                else:
                    # Predict if it is a positive or a negative comment
                    if CA.simple_predict(comment['message']):
                        graph.put_object(comment['id'], 'likes')
                        graph.put_comment(comment['id'], message='Thanks for Commenting.')
                        
                        print('Positive comment. Liking\n')
                    else:
                        print('It is a negative comment\n')
   
"""
print('For the first time')
print('====================================================')
reply_comments()
print('====================================================')
print('====================================================')
print('Sleeping for 10 Seconds')
time.sleep(10)
print('====================================================')
print('====================================================') 
print('For the second time')
print('====================================================')
reply_comments()
print('====================================================') 
"""