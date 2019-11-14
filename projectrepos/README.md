# Project Repository Functions

Scores of students enter into the Labs program every month. These students form dozens of teams to develop software. Each of these teams need Github repositories in which to maintain their code. These functions are responsible for managing the lifecycle of these repositories.

## provision_project_github_repos

This function is responsible for provisioning new repositories when needed. Labby checks the `Product Github Repos` table to see if there are any new repositories needed. Each row represents a repository needed by the team. The Github `Repo ID` is initially blanks and is set for the row when Labby provisions the repository.

### Repository Naming

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

### Adopting Repositories

Labby is also able to automatically adopt an existing repository that was created outside of Labby. Before provisioning a repository, Labby checks to see if there is already a repository that exists with the same name generated using the above naming convention. If there is, Labby assumes that is a repository that needs to be adopted and instead of creating a new repository, Labby simply uses the existing one and store its `Repo ID`
