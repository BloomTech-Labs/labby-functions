# Data Access Objects (DAO)

Labby needs to interact with all sorts of APIs to perform various functions. These interactions often require some sort of authentication, prepping of clients and other multiple steps before the actual API calls can be made. Also, the API providers for various resources that Labby interacts with will change over time.

The modules in this package are meant to insulate the rest of the Labby code from the details of the API interactions and the providers themselves. They are a collection of wrapper and helper functions to factor out some of the boilerplate code that's necessary to make API calls.

Think of it as a sort of an internal Labby API layer that allows Labby to conveniently do things across a bunch of other APIs.

## People

Data access functions that primarily deal with the People table in the Labs Data Model.

## Product Repos

Data access functions that primarily deal with the People table in the Labs Data Model.
