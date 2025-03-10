# Assumptions
1. No option for a cart. Order one item at a time.
2. All items have been pre registered in the database
3. Users of two types- retail and bulk, prices will be different for both. Ordering more than one pieces of an item is considered as bulk.
4. Delivery will be given a date, not part of e commerce system(third party).
5. For every third order, discount will be given.
6. Only new customer can be created, rest will be static.


Explaining creation of test cases-
With the above test cases, which were necessary to reduce unnecessary complexity in the app, we can explain the creation of classes and testcases.<br>

Only two types of users, one class for Orders and another for Products.
Simple functions as required.<br>
Now, while defining test cases- every function I made- both valid and invalid options. Checked with the respective output, or exceptions.
