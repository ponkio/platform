# Scrapes public sites for info and stores into database
# github
# gitlab
## Public sources should be re-scrapped atleast once a month to account for people modifying repo visibility

from scrape_github import scrape_github


scrape_github.populate_public_repos(106462)