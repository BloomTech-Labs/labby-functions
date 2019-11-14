# Github

Github is a core service for Lambda Labs project teams. All teams maintain their code bases in Github. Scores of students enter into the Labs program every month. These students form dozens of teams to develop software. Each of these teams need Github repositories in which to maintain their code.

Labby handles much of the complexity of managing the hundreds of Github repositories used in Labs. Labby manages the life-cycle of Github repositories to match the life-cycle of products and projects.

## Provisioning Repositories

Labby is responsible for provisioning new repositories when needed. Labby checks the `Product Github Repos` table to see if there are any new repositories needed. Each row represents a repository needed by the team. The Github `Repo ID` is initially blanks and is set for the row when Labby provisions the repository.

## Adopting Repositories

Labby is also able to automatically adopt an existing repository that was created outside of Labby. Before provisioning a repository, Labby checks to see if there is already a repository that exists with the same name generated using the above naming convention. If there is, Labby assumes that is a repository that needs to be adopted and instead of creating a new repository, Labby simply uses the existing one and store its `Repo ID`

## Repository Naming

Repositories are named with a specific naming convention: `<Product Name>-<Custom Postfix>-<Purpose>`

- Special characters are removed from the final repository name for aesthetic reasons.
- The custom postfix can be used to differentiate repositories for the same product with the same purpose.
- The purpose is a special postfix to help identify the code in the repository:
  - FRONTEND        = "-fe"
  - BACKEND         = "-be"
  - DATA_SCIENCE    = "-ds"
  - MOBILE          = "-mobile"
  - IOS             = "-ios"
  - ANDROID         = "-android"
  - SITE            = "-site"

## Gathering Metrics

The functions in this module are responsible for periodically gathering and storing Github metrics for use by reporting and operational tools.

Metrics:

- Push events

These functions are implemented as a combination of event-driven web-hooks, called by Github in real-time, in addition to functions that periodically poll Github to gather metrics not pushed by Github.

## Github DAO

The DAO in this module enables easy access to the Code Climate API.
