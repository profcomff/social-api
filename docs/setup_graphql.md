## GraphQL get some ID's instriction
You can find this many of id's with only
with GraphQL requests ([use Explorer](https://docs.github.com/ru/graphql/overview/explorer)):


```graphql
# This query return scrum project's id's (PROJECT_NODE_ID). Bot only can add issue only to one project
{organization(login: "GH_ORGANIZATION_NICKNAME") {
    projectsV2(first: 100) {
      edges {
        node {
          title
          id
          public
}}}}}
```
```graphql
# Use PROJECT_NODE_ID for next request.
{node(id: "PROJECT_NODE_ID") {
    ... on ProjectV2 {
      fields(first: 20) {
        nodes {
          ... on ProjectV2Field {
            id
            name
          }
          ... on ProjectV2IterationField {
            id
            name
            configuration {
              iterations {
                startDate
                id
              }
            }
          }
          ... on ProjectV2SingleSelectField {
            id
            name
            options {
                id
                name
}}}}}}}
```