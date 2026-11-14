"""Build both language editions: python build.py [output-directory].

No network access, external Python package, or Ruby installation is required.
"""
from pathlib import Path, PurePosixPath
from string import Template
from html import escape
import json
import posixpath
import shutil
import sys

ROOT = Path(__file__).resolve().parent
DEST = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / 'site'
CANONICAL = 'https://tienan.github.io/ma-lab/'
PAGES = ('home', 'research', 'people', 'publications', 'software', 'teaching', 'about', 'contact')
LOCALES = {
    'en': {
        'lang': 'en', 'page_title': 'Shiyang Ma | Statistical Genetics & Biostatistics',
        'description': 'Shiyang Ma — statistical genetics and biostatistics at Shanghai Jiao Tong University. Research, selected publications, software and teaching.',
        'skip': 'Skip to content', 'home_label': 'MaLab home', 'nav_home': 'Home',
        'language_label': 'Language', 'navigation_label': 'Main navigation', 'menu': 'Menu', 'menu_open': 'Open menu',
        'nav_research': 'Research', 'nav_publications': 'Publications', 'nav_software': 'Software',
        'nav_people': 'People', 'people_intro': 'Ma Lab leadership, staff and students.',
        'nav_teaching': 'Teaching', 'nav_about': 'About', 'nav_contact': 'Contact',
        'university': 'Shanghai Jiao Tong University',
        'hero_subtitle': 'Statistical genetics and biostatistics',
        'hero_description': 'Developing statistical and computational methods for high-dimensional genetic and genomic data, variable selection, and clinical research.',
        'explore_research': 'Explore research', 'selected_publications': 'Selected publications',
        'profiles_label': 'Academic profiles', 'portrait_alt': 'Portrait from Shiyang Ma’s academic homepage',
        'portrait_role': 'Associate Professor',
        'research_intro': 'The work spans methods for genetic and genomic data, variable selection and clinical research.',
        'genetics_figure_alt': 'Manhattan plot of simulated associations across 22 chromosomes. The dashed line marks P = 5 × 10⁻⁸.',
        'biostatistics_figure_alt': 'Kaplan–Meier survival curves with 95% confidence bands for two simulated groups.',
        'publications_heading': 'Selected publications',
        'publications_intro': 'Selected work in statistical genetics, biostatistics and clinical research.',
        'search_label': 'Search publications', 'search_placeholder': 'Search title, author, journal…',
        'year_label': 'Year', 'all_years': 'All years',
        'empty_state': 'No publications match your search. Try another title, author or year.',
        'full_citation': 'Full citation',
        'noscript': 'All publications are shown. Enable JavaScript to search and filter this list.',
        'software_intro': 'R packages and research datasets for genetic association studies.',
        'view_repository': 'View repository', 'view_dataset': 'View dataset on Zenodo',
        'teaching_intro': 'Courses and guest lectures at Shanghai Jiao Tong University.',
        'about_heading': 'Academic profile',
        'experience_heading': 'Experience', 'education_heading': 'Education', 'students_heading': 'Students',
        'pi_role': 'PI', 'sub_pi_role': 'Sub-PI', 'secretary_role': 'Lab Secretary / 秘书',
        'students_moved': 'Find the students on the People page.',
        'talks_heading': 'Invited talks', 'journal_review_heading': 'Journal review',
        'back_to_top': 'Back to top',
        'dynamic': {
            'count_singular': '{count} publication', 'count_plural': '{count} publications',
            'showing': ' · showing {shown}', 'show_all': 'Show all {count} publications',
            'menu_closed': 'Menu', 'menu_open': 'Close',
            'menu_open_label': 'Open menu', 'menu_close_label': 'Close menu'
        }
    },
    'zh': {
        'lang': 'zh-CN', 'page_title': 'Shiyang Ma｜统计遗传学与生物统计学',
        'description': 'Shiyang Ma 的学术主页：上海交通大学统计遗传学与生物统计学研究、精选论文、科研软件及教学。',
        'skip': '跳至正文', 'home_label': 'MaLab 首页', 'nav_home': '首页',
        'language_label': '语言', 'navigation_label': '主导航', 'menu': '菜单', 'menu_open': '打开菜单',
        'nav_research': '研究方向', 'nav_publications': '精选论文', 'nav_software': '科研软件',
        'nav_people': '团队', 'people_intro': 'Ma Lab 负责人、秘书与学生。',
        'nav_teaching': '教学', 'nav_about': '关于', 'nav_contact': '联系',
        'university': '上海交通大学', 'hero_subtitle': '统计遗传学与生物统计学',
        'hero_description': '围绕高维遗传与基因组数据、变量选择和临床研究，开发统计与计算方法。',
        'explore_research': '了解研究方向', 'selected_publications': '查看精选论文',
        'profiles_label': '学术与专业主页', 'portrait_alt': '来自 Shiyang Ma 原学术主页的肖像',
        'portrait_role': '副教授',
        'research_intro': '研究涵盖遗传与基因组数据分析、变量选择，以及临床研究中的统计方法。',
        'genetics_figure_alt': '模拟全基因组关联分析的曼哈顿图，横轴为 22 条常染色体，虚线标示 P = 5 × 10⁻⁸。',
        'biostatistics_figure_alt': '两个模拟组的 Kaplan–Meier 生存曲线，含 95% 置信带。',
        'publications_heading': '精选论文',
        'publications_intro': '统计遗传学、生物统计学与临床研究领域的精选工作。',
        'search_label': '检索论文', 'search_placeholder': '搜索中英文题名、作者或期刊…',
        'year_label': '年份', 'all_years': '全部年份',
        'empty_state': '未找到匹配的论文，请尝试其他题名、作者或年份。',
        'full_citation': '完整引文（英文原文）',
        'noscript': '当前显示全部论文。启用 JavaScript 后可检索并按年份筛选。',
        'software_intro': '用于遗传关联研究的 R 软件包与研究数据。',
        'view_repository': '查看代码仓库', 'view_dataset': '在 Zenodo 查看数据',
        'teaching_intro': '在上海交通大学开设的课程及客座授课。',
        'about_heading': '关于',
        'experience_heading': '工作经历', 'education_heading': '教育背景', 'students_heading': '学生',
        'pi_role': 'PI', 'sub_pi_role': 'Sub-PI', 'secretary_role': '秘书 / Lab Secretary',
        'students_moved': '前往团队页查看学生。',
        'talks_heading': '受邀报告', 'journal_review_heading': '期刊审稿',
        'back_to_top': '返回顶部',
        'dynamic': {
            'count_singular': '共 {count} 篇论文', 'count_plural': '共 {count} 篇论文',
            'showing': ' · 显示前 {shown} 篇', 'show_all': '显示全部 {count} 篇论文',
            'menu_closed': '菜单', 'menu_open': '收起',
            'menu_open_label': '打开菜单', 'menu_close_label': '关闭菜单'
        }
    }
}
RESEARCH_LAYOUT = {
    'research-interests-1': ('statistical-genetics', 'genetics_figure_alt', 'software'),
    'research-interests-2': ('biostatistics', 'biostatistics_figure_alt', 'publications'),
}
PEOPLE = (
    ('portrait.jpeg', '马诗洋', 'Shiyang Ma', 'pi_role'),
    ('people/tienan-feng.jpg', '冯铁男', 'Tienan Feng', 'sub_pi_role'),
    ('people/xuequn-huang.jpg', '黄雪群', 'Xuequn Huang', 'secretary_role'),
)


def e(value):
    return escape(str(value or ''), quote=True)


def page_path(language, page):
    directory = PurePosixPath('zh' if language == 'zh' else '.')
    if page != 'home':
        directory /= page
    return directory / 'index.html'


def relative_href(current, target):
    return posixpath.relpath(target.as_posix(), start=current.parent.as_posix())


def canonical_url(path):
    directory = path.parent.as_posix()
    return CANONICAL if directory == '.' else f'{CANONICAL}{directory}/'


def prepare_content(data, english, language):
    labels = LOCALES[language]
    chinese = language == 'zh'
    substitutions = {key: e(value) for key, value in labels.items() if isinstance(value, str)}
    substitutions.update({
        'en_current': '' if chinese else ' aria-current="page"',
        'zh_current': ' aria-current="page"' if chinese else '',
        'name': e(english['profile']['name']),
        'i18n_json': json.dumps(labels['dynamic'], ensure_ascii=False).replace('</', '<\\/'),
    })
    social_labels = {'Google Scholar': '谷歌学术'} if chinese else {}
    social = ''.join(f'<a href="{e(x["url"])}" target="_blank" rel="noopener noreferrer">{e(social_labels.get(x["label"], x["label"]))} <span aria-hidden="true">↗</span></a>' for x in english['profile']['social_links'])
    research = []
    research_page = page_path(language, 'research')
    for topic in data['research_interests']:
        figure, alt_label, section = RESEARCH_LAYOUT[topic['id']]
        image = relative_href(research_page, PurePosixPath('assets') / f'{figure}-{language}.png')
        href = relative_href(research_page, page_path(language, section))
        research.append(f'''<article class="research-item">
          <figure class="research-figure">
            <img src="{image}" width="900" height="480" alt="{e(labels[alt_label])}">
          </figure>
          <div class="research-copy">
            <h3>{e(topic['title'])}</h3>
            <p>{e(topic['description'])}</p>
            <a class="text-link" href="{href}">{e(labels[f'nav_{section}'])} <span aria-hidden="true">→</span></a>
          </div>
        </article>''')
    original_publications = {x['id']: x for x in english['publications']}
    if len(data['publications']) != len(original_publications):
        raise ValueError('Both language editions must contain the same publication records.')
    publications = []
    for x in data['publications']:
        original = original_publications[x['id']]
        year = original['year']
        title = e(x['title'])
        if original['url']:
            title = f'<a href="{e(original["url"])}" target="_blank" rel="noopener noreferrer">{title}<span aria-hidden="true"> ↗</span></a>'
        journal = f'<p class="publication-journal" lang="en">{e(original["journal"])}</p>' if original['journal'] else ''
        # Keep author emphasis and footnote markers from the original English HTML.
        authors = original['citation_html'].split(f'({year})', 1)[0].strip()
        search_text = ' '.join([original['citation'], x['title'], x.get('text', '')]).lower()
        publications.append(f'<li class="publication" data-year="{year}" data-search="{e(search_text)}"><span class="publication-year">{year}</span><div class="publication-body"><h3 class="publication-title">{title}</h3><p class="publication-authors" lang="en">{authors}</p>{journal}<details class="citation-details"><summary>{e(labels["full_citation"])}</summary><p lang="en">{original["citation_html"]}</p></details></div></li>')
    software = []
    for item in data['software']:
        action = labels['view_dataset' if item['id'] == 'software-4' else 'view_repository']
        url, title, description = (e(item[key]) for key in ('url', 'title', 'description'))
        software.append(f'''<article class="software-item">
          <h3><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></h3>
          <p>{description}</p>
          <a class="text-link" href="{url}" target="_blank" rel="noopener noreferrer">{e(action)} <span aria-hidden="true">↗</span></a>
        </article>''')
    teaching = ''.join(f'<div class="teaching-row"><div class="teaching-title">{x["html"]}</div><span class="teaching-detail">{e(x["semester"])}</span></div>' for x in data['teaching'])

    def timeline(items, date_key):
        rows = []
        for item in items:
            date = str(item.get(date_key) or '')
            if chinese:
                date = date.replace('present', '至今')
            rows.append(f'<article class="timeline-item"><span class="timeline-year">{e(date)}</span><div class="timeline-content">{item["html"]}</div></article>')
        return ''.join(rows)

    students = []
    original_students = {x['id']: x for x in english['students']}
    for item in data['students']:
        name = original_students[item['id']]['name']
        text = item['text'].removeprefix(name).lstrip(',， \u3000')
        description = e(text)
        if profile := item.get('advisor_homepage'):
            before, mention, after = text.partition(profile['mention'])
            if not mention:
                raise ValueError(f'Advisor name missing from {item["id"]} in {language}.')
            link = f'<a href="{e(profile["url"])}">{e(profile.get("label", mention))}</a>'
            description = e(before) + link + e(after)
        students.append(f'<li class="student-item"><h3>{e(name)}</h3><p>{description}</p></li>')
    talks = ''.join(f'<div class="talk-row"><span>{e(x["date"])}</span><p>{e(x["title"])}</p></div>' for x in data['invited_talks'])
    total = len(publications)
    substitutions.update({
        'social_links': social, 'research': '\n'.join(research), 'publications': '\n'.join(publications),
        'year_options': ''.join(f'<option value="{year}">{year}</option>' for year in sorted({x['year'] for x in english['publications']}, reverse=True)),
        'software': '\n'.join(software), 'teaching': teaching,
        'experience': timeline(data['experience'], 'period'), 'education': timeline(data['education'], 'year'),
        'students': ''.join(students), 'talks': talks,
        'talk_count': f'{len(data["invited_talks"])} 场报告' if chinese else f'{len(data["invited_talks"])} talks',
        'journal_review': data['journal_review']['html'],
        'contact_intro': '<p>' + e(data['contact']['invitation']) + '</p>',
        'email': e(english['contact']['email']),
        'address': '<p>' + '<br>'.join(e(x) for x in data['contact']['address_lines']) + '</p>',
        'initial_count': labels['dynamic']['count_plural'].format(count=total),
        'show_all': labels['dynamic']['show_all'].format(count=total),
    })
    return substitutions


def render_page(content, language, page, template, section):
    labels = LOCALES[language]
    path = page_path(language, page)
    assets_prefix = relative_href(path, PurePosixPath('assets')) + '/'
    localized = {lang: page_path(lang, page) for lang in ('en', 'zh')}
    section_hrefs = {slug: relative_href(path, page_path(language, slug)) for slug in PAGES}
    nav_links = []
    for slug, href in section_hrefs.items():
        classes = 'nav-link nav-contact' if slug == 'contact' else 'nav-link'
        active = ' aria-current="page"' if slug == page else ''
        nav_links.append(f'<a class="{classes}" href="{href}" data-page-link="{slug}"{active}>{e(labels[f"nav_{slug}"])}</a>')

    values = {
        **content,
        'page': page,
        'assets_prefix': assets_prefix,
        'canonical': canonical_url(path),
        'alternate_en': canonical_url(localized['en']),
        'alternate_zh': canonical_url(localized['zh']),
        'en_href': relative_href(path, localized['en']),
        'zh_href': relative_href(path, localized['zh']),
        'home_href': section_hrefs['home'],
        'research_href': section_hrefs['research'],
        'publications_href': section_hrefs['publications'],
        'people_href': section_hrefs['people'],
        'nav_links': '\n      '.join(nav_links),
        'banner': '',
    }
    if page == 'home':
        values['banner'] = f'<div class="lab-banner"><img src="{assets_prefix}lab-banner.jpg" alt="" width="2172" height="724" fetchpriority="high"></div>'
    else:
        values['page_title'] = f'{e(labels[f"nav_{page}"])} | {content["name"]}'
        values['description'] = content.get(f'{page}_intro', content['description'])
    if page == 'people':
        cards = []
        for image, name_zh, name_en, role in PEOPLE:
            if language == 'zh':
                name = f'{e(name_zh)} <span lang="en">{e(name_en)}</span>'
            else:
                name = f'{e(name_en)} <span lang="zh-CN">{e(name_zh)}</span>'
            cards.append(f'''<li class="person-card">
          <img src="{assets_prefix}{image}" alt="" class="{role.replace('_', '-')}">
          <h2>{name}</h2>
          <p>{e(labels[role])}</p>
        </li>''')
        values['people_cards'] = '\n'.join(cards)
    values['page_content'] = section.substitute(values).strip()
    return path, template.substitute(values)


def main():
    english = json.loads((ROOT / 'content-en.json').read_text(encoding='utf-8-sig'))
    chinese = json.loads((ROOT / 'content-zh.json').read_text(encoding='utf-8-sig'))
    template = Template((ROOT / 'template.html').read_text(encoding='utf-8'))
    sections = {page: Template((ROOT / f'pages/{page}.html').read_text(encoding='utf-8')) for page in PAGES}
    pages = []
    for language, data in (('en', english), ('zh', chinese)):
        content = prepare_content(data, english, language)
        pages.extend(render_page(content, language, page, template, sections[page]) for page in PAGES)
    # Render both editions before writing any pages.
    DEST.mkdir(parents=True, exist_ok=True)
    assets = DEST / 'assets'
    assets.mkdir(exist_ok=True)
    figures = tuple(f'{figure}-{language}.png' for figure, _, _ in RESEARCH_LAYOUT.values() for language in LOCALES)
    people_assets = (image for image, *_ in PEOPLE)
    asset_names = ('site.css', 'site.js', 'favicon.svg', 'lab-banner.jpg', *people_assets, *figures)
    for name in asset_names:
        target = assets / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    for path, html in pages:
        destination = DEST.joinpath(*path.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(html, encoding='utf-8')
    (DEST / '_config.yml').write_text(
        'title: Shiyang Ma\n'
        'description: Statistical genetics and biostatistics\n'
        'author: Shiyang Ma\n'
        'url: "https://tienan.github.io"\n'
        'baseurl: "/ma-lab"\n'
        'exclude:\n  - _source\n  - README.md\n',
        encoding='utf-8',
    )
    print(json.dumps({'built': True, 'directory': str(DEST), 'languages': ['en', 'zh-CN'], 'pages': [path.as_posix() for path, _ in pages], 'publication_count_per_language': len(english['publications']), 'assets': len(asset_names)}, ensure_ascii=True))


if __name__ == '__main__':
    main()
