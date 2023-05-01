from prefect.filesystems import GitHub
from config import github_url

# Make the block
github_block = GitHub(
    name = 'github-zoom',
    repository = github_url
)

# Save the block
github_block.save('github-zoom', overwrite=True)
