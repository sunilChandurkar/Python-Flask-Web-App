Please unzip the oauth folder.

cd to the oauth directory

type vagrant up

then after bagrant is up type vagrant ssh

type cd /vagrant

to setup the database type: python database_setup.py

to create a few categories type: python insert_categories.py

to run the app type: python project.py

The User can Log in using Facebook Login.

The home page shows a list of Sports Item Categories and a list of Items belonging to Categories.

The User can click on a Category to show items in the category.

The User can then click on an item to view the details.

If a User has created a particular item and is loggen in the User can edit or delete the item.