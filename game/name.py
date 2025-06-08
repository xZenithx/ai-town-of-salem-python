# name.py
# Utility to pick a random player name
import random

NAMES = [
    # Common English names
    "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Hank", "Ivy", "Jack",
    "Karen", "Leo", "Mona", "Nina", "Oscar", "Paul", "Quinn", "Rita", "Sam", "Tina",
    "Uma", "Vince", "Wendy", "Xander", "Yara", "Zane",
    # More names
    "Aaron", "Abby", "Adrian", "Aiden", "Alex", "Alexa", "Amber", "Amelia", "Amy", "Andrea",
    "Andrew", "Angela", "Annie", "Anthony", "April", "Ashley", "Austin", "Barry", "Becky", "Ben",
    "Brandon", "Brenda", "Brian", "Brianna", "Brittany", "Brooke", "Bryan", "Caleb", "Cameron", "Carl",
    "Carla", "Carmen", "Carol", "Caroline", "Carter", "Cathy", "Chad", "Chloe", "Chris", "Christina",
    "Christine", "Cindy", "Clara", "Clarence", "Clayton", "Cliff", "Clint", "Colin", "Connor", "Courtney",
    "Craig", "Crystal", "Curtis", "Cynthia", "Dale", "Dan", "Dana", "Daniel", "Danielle", "Darren",
    "Dave", "David", "Debbie", "Deborah", "Dennis", "Derek", "Destiny", "Don", "Donna", "Doris",
    "Dorothy", "Doug", "Dylan", "Ed", "Eddie", "Edith", "Edward", "Elaine", "Elena", "Eli", "Elijah",
    "Elizabeth", "Ella", "Ellen", "Emily", "Eric", "Erica", "Erik", "Erin", "Ethan", "Eugene", "Faith",
    "Felicia", "Fiona", "Florence", "Francis", "Gabriel", "Gail", "Gavin", "Gene", "Geoff", "George",
    "Georgia", "Gerald", "Gina", "Glen", "Gloria", "Gordon", "Greg", "Hailey", "Haley", "Hannah",
    "Harold", "Harry", "Heather", "Heidi", "Helen", "Henry", "Holly", "Hope", "Howard", "Hunter",
    "Irene", "Isaac", "Isabel", "Isabella", "Jackie", "Jacob", "Jade", "Jake", "James", "Jamie",
    "Jan", "Jane", "Janet", "Janice", "Jared", "Jason", "Jean", "Jeff", "Jeffrey", "Jenna", "Jennifer",
    "Jenny", "Jeremiah", "Jeremy", "Jerry", "Jesse", "Jessica", "Jill", "Joan", "Joanna", "Joe",
    "Joel", "John", "Johnny", "Jon", "Jonathan", "Jordan", "Jose", "Joseph", "Josh", "Joshua", "Joy",
    "Joyce", "Juan", "Judith", "Judy", "Julia", "Julian", "Julie", "Justin", "Kara", "Karen", "Katelyn",
    "Kathleen", "Kathy", "Katie", "Kayla", "Keith", "Kelly", "Ken", "Kendra", "Kenneth", "Kevin",
    "Kim", "Kimberly", "Kirk", "Kristen", "Kristin", "Kyle", "Lance", "Larry", "Laura", "Lauren",
    "Laurie", "Leah", "Lee", "Leonard", "Leslie", "Liam", "Linda", "Lindsay", "Lisa", "Logan",
    "Lori", "Louis", "Lucas", "Luke", "Lydia", "Lynn", "Madison", "Maggie", "Manuel", "Marc",
    "Margaret", "Maria", "Marie", "Marilyn", "Marion", "Mark", "Marlene", "Marsha", "Martha", "Martin",
    "Marvin", "Mary", "Mason", "Matt", "Matthew", "Megan", "Melanie", "Melissa", "Melvin", "Meredith",
    "Mia", "Michael", "Michelle", "Mick", "Mickey", "Mike", "Mindy", "Miranda", "Mitchell", "Molly",
    "Monica", "Morgan", "Nancy", "Natalie", "Nathan", "Neil", "Nicholas", "Nicole", "Noah", "Norma",
    "Olivia", "Pam", "Pamela", "Pat", "Patricia", "Patrick", "Pauline", "Peggy", "Penny", "Peter",
    "Phil", "Philip", "Phillip", "Rachel", "Ralph", "Randy", "Ray", "Raymond", "Rebecca", "Regina",
    "Renee", "Rhonda", "Richard", "Rick", "Rita", "Rob", "Roberta", "Robert", "Robin", "Roger",
    "Ron", "Ronald", "Rose", "Ross", "Roy", "Ruby", "Russell", "Ruth", "Ryan", "Sally", "Sammy",
    "Sandra", "Sara", "Sarah", "Scott", "Sean", "Shane", "Shannon", "Sharon", "Sheila", "Shelby",
    "Sherri", "Sherry", "Shirley", "Sidney", "Sierra", "Sofia", "Sonia", "Sophie", "Spencer", "Stacy",
    "Stanley", "Stephanie", "Stephen", "Steve", "Steven", "Sue", "Summer", "Susan", "Suzanne", "Sydney",
    "Sylvia", "Tammy", "Tanya", "Tara", "Taylor", "Ted", "Teresa", "Terri", "Terry", "Thelma", "Theresa",
    "Thomas", "Tiffany", "Tim", "Timothy", "Tina", "Todd", "Tom", "Toni", "Tony", "Tracy", "Travis",
    "Trent", "Trevor", "Troy", "Tyler", "Valerie", "Vanessa", "Vera", "Vernon", "Veronica", "Vicki",
    "Vicky", "Victor", "Victoria", "Vincent", "Virginia", "Vivian", "Wade", "Walter", "Wanda", "Wayne",
    "Wesley", "Will", "William", "Willie", "Yolanda", "Yvonne", "Zach", "Zachary", "Fell"
]

def pick_random_name() -> str:
    """Return a random name from the NAMES list."""
    return random.choice(NAMES)

def pick_multiple_names(count: int) -> list[str]:
    """Return a list of unique random names from the NAMES list."""
    if count > len(NAMES):
        raise ValueError("Requested more unique names than available in the list.")
    return random.sample(NAMES, count)
