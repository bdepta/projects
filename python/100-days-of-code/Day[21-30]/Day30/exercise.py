
#* Exercise 1
# Issue
# We've got some buggy code. Try running the code. The code will crash and give you an IndexError. This is because we're looking through the list of fruits for an index that is out of range.

fruits = ["Apple", "Pear", "Orange"]
def make_pie(index):
    try:
      fruit = fruits[index]
    except IndexError:
       print(f"Fruit pie")
    else:  
      print(fruit + " pie")


# 🚨 Do not change the code below
make_pie(4)

#TODO Exercise 2
# We've got some buggy code, try running the code. The code will crash and give you a KeyError. This is because some of the posts in the facebook_posts don't have any "Likes".
[{'Likes': 21, 'Comments': 2}, {'Likes': 13, 'Comments': 2, 'Shares': 1}, {'Likes': 33, 'Comments': 8, 'Shares': 3}, {'Comments': 4, 'Shares': 2},{'Comments': 1, 'Shares': 1}, {'Likes': 19, 'Comments': 3}]
total_likes = 0
# TODO: Catch the KeyError exception
for post in facebook_posts:
  try:
    total_likes = total_likes + post['Likes']
  except KeyError:
    total_likes = total_likes + 0

print(total_likes)