# codebrew2021

### Live website
[growocery.herokuapp.com](growocery.herokuapp.com)

### How to run the app
1. Create a Python virtual environment.
```
virtualenv venv
source venv/bin/activate
```
2. Install packagages. 
```
pip install -r requirements.txt
```
3. Run migrations.
```
python manage.py makemigrations
python manage.py migrate
```
4. Start the app.
```
python manage.py runserver
```

### Access populated suburb as an example
Create a new account with the postcode 2148 to see the application working in action.




## Inspiration
Our idea for Growocery was inspired by how food insecurity and inequality in access to food became even more prevalent during the COVID-19 pandemic. One of the key components of food insecruity was inadequate access to shops selling healthy food and groceries. We found out that 61.6%  living in inner regional areas live more than 1.6km to the nearest grocer. These households - often in lower socio-economic areas - are located in 'food deserts', where grocery stores are far while fast food stores are near, limiting their options to convenient but unhealthy foods.

We wanted to encourage members of the community to eat and cook healthier, by giving them that convenience. We do this by facilitating them with a platform to pool their shopping lists together in order to get privilleges such as cheap or even free delivery and cheaper prices through buying items in bulk.

## What it does
Growocery is a platform to pool your shopping lists with your neighbours! Users are assigned to a community with other users in their area, and their grocery lists are consolidated to access cheaper goods and split delivery fees. 

## How we built it
- Planning: Prior to beginning development, we devised use case texts for our application to understand the user flow. We also created an entity relation diagram to illustrate relationships between different objects in the application to prevent frequent database migrations during development. This culminated in a lofi mockup on Figma. 
- Development: The team was split internally into frontend and backend developers. The backend developer worked on implementing functionality, starting from an authentication system, all the way to implementing an algorithm to combine multiple orders for bulk buying. Meanwhile, the frontend developers drafted hifi mockups using Figma to incorporate style and branding, and implemented the pages using HTML and CSS. 
- Data injection: To enhance the demo, we manually scraped Coles catalogue items and wrote a script to insert them into the SQLite database, so that the catalogue could be populated for the demo. This also allows us to repopulate the database from scratch in case of any errors.
- Deployment: After the user flow was built and functional, we deployed the application onto Heroku, marking the conclusion of the development of Growocery. 

## Challenges we ran into
- Unbounded Minimizing Knapsack problem - solved recursively
- Scraping grocery chain websites - we went into the project having Python’s BeautifulSoup at the ready in order to scrape data for our items catalogue. It turns out most major grocery chains block web scraping by detecting that a scraper is requesting the information and sending back errors. So instead, we had to manually scrape item information and write a script to load them into the database for our items catalogue.
- We had quite complex database models

## Accomplishments that we're proud of
- The complex database models that actually work
- Functional and aesthetically pleasing User Experience 
- Our project name: GroWocery, need we say more

## What we learned
-  Web Development using Django - This was the team’s first or second time using Django for web development. Building Growcery from scratch has been a valuable practical learning experience. 
- Project management using Jira and Git - In order to manage concurrent development and avoid merge conflicts, we stuck to the gitflow workflow of implementing features. Exposure to Jira and Git allowed us to work in an industry-like setting. 
- Background research about food deserts - We’d each had heard about or visited places considered to be ‘food deserts’. It was quite eye-opening to learn about the long-term health issues that communities face due to.

## Functional Features:
- User authentication
- Grouping of users into communities based on postcode
- Integrated shopping catalogue for 2 major retailers (Coles & Woolworths)
- Searchbar for products
- Adding/ removing items from shopping list
- Pooling shopping list with neighbours
- Consolidation of selected products into bulk goods
- Automatic calculation of delivery fees
- Automatic generation of invoices
- Volunteering to be responsible for group purchase


## What's next for Growocery
- Scraping / utilizing developer APIs of major grocery retailer sites for information in out items catalogue 
- Online payment system.
- Gamification of the interface by incorporating reward incentives. 
- Extending into other retailers, including wholesale retailers and local markets
- Responsive web design
- Notifications for users to keep them up to date with their community
- Automating the ordering process


https://devpost.com/software/growocery
