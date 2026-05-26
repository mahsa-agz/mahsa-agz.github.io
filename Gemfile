source "https://rubygems.org"

# GitHub Pages uses a pinned set of gem versions ,  using this metagem
# locks our local preview to the same versions that build the live site.
# See: https://pages.github.com/versions/
gem "github-pages", group: :jekyll_plugins

# Plugins enabled in _config.yml ,  included via github-pages, listed here
# for clarity.
group :jekyll_plugins do
  gem "jekyll-sitemap"
  gem "jekyll-seo-tag"
end

# Windows + JRuby support for the `webrick` server (used by `jekyll serve`).
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", "~> 1.2"
  gem "tzinfo-data"
end
gem "wdm", "~> 0.1.1", platforms: [:mingw, :x64_mingw, :mswin]
gem "webrick", "~> 1.7"
