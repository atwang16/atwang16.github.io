# Austin Wang's Personal Website

This is a jinja-based build for a personal academic website, based on an earlier version of [Nick Vincent's personal website](https://github.com/nickmvincent/simple_research_website).

## Local Development

Setup your python 3.11 environment:

```bash
python3.11 -m venv venv
source venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Build the website:
```bash
python generate_site.py --build-site
```

To open the website locally, go to [output/index.html](output/index.html).

## To Do

- [ ] Create a page for all of the blog posts
- [ ] Port remaining blog posts from old website
- [ ] Create resumé from `website.yaml`
- [ ] Create a dark mode for the website
