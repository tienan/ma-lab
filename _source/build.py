"""Build both language editions: python build.py [output-directory].

No network access, external Python package, or Ruby installation is required.
"""
from pathlib import Path
from string import Template
from html import escape
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parent
DEST = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / 'site'
CANONICAL = 'https://tienan.github.io/ma-lab/'
LOCALES = {
    'en': {
        'lang': 'en', 'page_title': 'Shiyang Ma | Statistical Genetics & Biostatistics',
        'description': 'Shiyang Ma — statistical genetics and biostatistics at Shanghai Jiao Tong University. Research, selected publications, software and teaching.',
        'skip': 'Skip to content', 'home_label': 'Shiyang Ma home', 'brand_caption': 'STATISTICS & GENOMICS',
        'language_label': 'Language', 'navigation_label': 'Main navigation', 'menu': 'Menu', 'menu_open': 'Open menu',
        'nav_research': 'Research', 'nav_publications': 'Publications', 'nav_software': 'Software',
        'nav_teaching': 'Teaching', 'nav_about': 'About', 'nav_contact': 'Contact',
        'university': 'Shanghai Jiao Tong University',
        'hero_subtitle': 'Statistical genetics.<br>Biostatistics.',
        'hero_description': 'Developing statistical and computational methods for high-dimensional genetic and genomic data, variable selection, and clinical research.',
        'explore_research': 'Explore research', 'selected_publications': 'Selected publications',
        'profiles_label': 'Academic profiles', 'portrait_alt': 'Portrait from Shiyang Ma’s academic homepage',
        'portrait_role': 'Associate Professor', 'discipline_methods': 'Statistical methods',
        'discipline_genomics': 'Genetic & genomic data', 'discipline_clinical': 'Clinical research',
        'research_kicker': '01 / RESEARCH', 'research_heading': 'Methods meet discovery.',
        'research_intro': 'Two complementary directions in statistical research.',
        'publications_kicker': '02 / SELECTED PUBLICATIONS', 'publications_heading': 'Selected research.',
        'publications_intro': 'Selected work in statistical genetics, biostatistics and clinical research.',
        'search_label': 'Search publications', 'search_placeholder': 'Search title, author, journal…',
        'year_label': 'Year', 'all_years': 'All years',
        'empty_state': 'No publications match your search. Try another title, author or year.',
        'full_citation': 'Full citation',
        'noscript': 'All publications are shown. Enable JavaScript to search and filter this list.',
        'software_kicker': '03 / SOFTWARE', 'software_heading': 'Research, made usable.',
        'software_intro': 'R packages and a browser for genetic association research.',
        'package_type': 'R PACKAGE', 'browser_type': 'RESULTS BROWSER',
        'view_repository': 'View repository', 'explore_results': 'Explore results',
        'teaching_kicker': '04 / TEACHING', 'teaching_heading': 'In the classroom.',
        'teaching_intro': 'Courses and guest lectures at Shanghai Jiao Tong University.',
        'about_kicker': '05 / ACADEMIC PROFILE', 'about_heading': 'People & perspective.',
        'experience_heading': 'Experience', 'education_heading': 'Education', 'students_heading': 'Students',
        'talks_heading': 'Invited talks', 'journal_review_heading': 'Journal review',
        'contact_kicker': '06 / GET IN TOUCH', 'contact_heading': 'Let’s connect.', 'back_to_top': 'Back to top',
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
        'skip': '跳至正文', 'home_label': 'Shiyang Ma 主页', 'brand_caption': '统计学 · 基因组学',
        'language_label': '语言', 'navigation_label': '主导航', 'menu': '菜单', 'menu_open': '打开菜单',
        'nav_research': '研究方向', 'nav_publications': '精选论文', 'nav_software': '科研软件',
        'nav_teaching': '教学', 'nav_about': '学术经历', 'nav_contact': '联系',
        'university': '上海交通大学', 'hero_subtitle': '统计遗传学<br>生物统计学',
        'hero_description': '围绕高维遗传与基因组数据、变量选择和临床研究，开发统计与计算方法。',
        'explore_research': '了解研究方向', 'selected_publications': '查看精选论文',
        'profiles_label': '学术与专业主页', 'portrait_alt': '来自 Shiyang Ma 原学术主页的肖像',
        'portrait_role': '副教授', 'discipline_methods': '统计方法',
        'discipline_genomics': '遗传与基因组数据', 'discipline_clinical': '临床研究',
        'research_kicker': '01 / 研究方向', 'research_heading': '以统计方法，探索科学问题。',
        'research_intro': '两个相互补充的统计研究方向。',
        'publications_kicker': '02 / 精选论文', 'publications_heading': '研究成果。',
        'publications_intro': '统计遗传学、生物统计学与临床研究领域的精选工作。',
        'search_label': '检索论文', 'search_placeholder': '搜索中英文题名、作者或期刊…',
        'year_label': '年份', 'all_years': '全部年份',
        'empty_state': '未找到匹配的论文，请尝试其他题名、作者或年份。',
        'full_citation': '完整引文（英文原文）',
        'noscript': '当前显示全部论文。启用 JavaScript 后可检索并按年份筛选。',
        'software_kicker': '03 / 科研软件', 'software_heading': '让研究方法更易使用。',
        'software_intro': '用于遗传关联研究的 R 软件包与结果浏览器。',
        'package_type': 'R 软件包', 'browser_type': '结果浏览器',
        'view_repository': '查看代码仓库', 'explore_results': '浏览研究结果',
        'teaching_kicker': '04 / 教学', 'teaching_heading': '课堂与教学。',
        'teaching_intro': '在上海交通大学开设的课程及客座授课。',
        'about_kicker': '05 / 学术经历', 'about_heading': '学术经历与学生。',
        'experience_heading': '工作经历', 'education_heading': '教育背景', 'students_heading': '学生',
        'talks_heading': '受邀报告', 'journal_review_heading': '期刊审稿',
        'contact_kicker': '06 / 联系', 'contact_heading': '欢迎联系。', 'back_to_top': '返回顶部',
        'dynamic': {
            'count_singular': '共 {count} 篇论文', 'count_plural': '共 {count} 篇论文',
            'showing': ' · 显示前 {shown} 篇', 'show_all': '显示全部 {count} 篇论文',
            'menu_closed': '菜单', 'menu_open': '收起',
            'menu_open_label': '打开菜单', 'menu_close_label': '关闭菜单'
        }
    }
}


def e(value):
    return escape(str(value or ''), quote=True)


def art(kind):
    if kind == 0:
        paths = ''.join(f'<path d="M{x} 48 Q{x+35} {20 if i % 2 else 76} {x+70} 48"/>' for i, x in enumerate(range(0, 280, 35)))
        nodes = ''.join(f'<circle cx="{x}" cy="{48 + ((i % 3)-1)*15}" r="{3 if i % 2 else 4}"/>' for i, x in enumerate(range(12, 310, 25)))
        drawing = f'<g fill="none" stroke="currentColor" stroke-width="1">{paths}<path d="M0 48h320" stroke-dasharray="2 7"/></g><g fill="currentColor">{nodes}</g>'
    else:
        drawing = '<g fill="none" stroke="currentColor" stroke-width="1"><path d="M4 70h310M20 84V8" opacity=".35"/><path d="M20 65C70 65 80 20 135 26S220 55 300 10" stroke-width="2"/><path d="M20 76C70 76 80 31 135 37S220 66 300 21M20 54C70 54 80 9 135 15S220 44 300 0" opacity=".3"/></g>'
    return '<div class="research-art"><svg viewBox="0 0 320 90" aria-hidden="true">' + drawing + '</svg></div>'


def render(data, english, language, template):
    labels = LOCALES[language]
    chinese = language == 'zh'
    substitutions = {key: e(value) for key, value in labels.items() if isinstance(value, str)}
    substitutions['hero_subtitle'] = labels['hero_subtitle']
    substitutions.update({
        'assets_prefix': '../assets/' if chinese else 'assets/',
        'canonical': CANONICAL + ('zh/' if chinese else ''),
        'alternate_en': CANONICAL, 'alternate_zh': CANONICAL + 'zh/',
        'en_href': '../' if chinese else './', 'zh_href': './' if chinese else 'zh/',
        'en_file_href': '../index.html' if chinese else 'index.html',
        'zh_file_href': 'index.html' if chinese else 'zh/index.html',
        'en_current': '' if chinese else ' aria-current="page"',
        'zh_current': ' aria-current="page"' if chinese else '',
        'name': e(english['profile']['name']),
        'i18n_json': json.dumps(labels['dynamic'], ensure_ascii=False).replace('</', '<\\/'),
    })
    social_labels = {'Google Scholar': '谷歌学术'} if chinese else {}
    social = ''.join(f'<a href="{e(x["url"])}" target="_blank" rel="noopener noreferrer">{e(social_labels.get(x["label"], x["label"]))} <span aria-hidden="true">↗</span></a>' for x in english['profile']['social_links'])
    research = ''.join(f'<article class="research-item"><span class="item-number">0{i+1}</span><h3>{e(x["title"])}</h3><p>{e(x["description"])}</p>{art(i)}</article>' for i, x in enumerate(data['research_interests']))
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
    software = ''.join(f'<article class="software-item"><div class="software-meta"><span class="software-number">0{i+1}</span><span class="software-type">{e(labels["package_type"] if i < 3 else labels["browser_type"])}</span></div><h3><a href="{e(x["url"])}" target="_blank" rel="noopener noreferrer">{e(x["title"])}</a></h3><p>{e(x["description"])}</p><a class="text-link" href="{e(x["url"])}" target="_blank" rel="noopener noreferrer">{e(labels["view_repository"] if i < 3 else labels["explore_results"])} <span aria-hidden="true">↗</span></a></article>' for i, x in enumerate(data['software']))
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
        students.append(f'<div class="student-item"><h4>{e(name)}</h4><p>{e(text)}</p></div>')
    talks = ''.join(f'<div class="talk-row"><span>{e(x["date"])}</span><p>{e(x["title"])}</p></div>' for x in data['invited_talks'])
    total = len(publications)
    substitutions.update({
        'social_links': social, 'research': research, 'publications': '\n'.join(publications),
        'year_options': ''.join(f'<option value="{year}">{year}</option>' for year in sorted({x['year'] for x in english['publications']}, reverse=True)),
        'software': software, 'teaching': teaching,
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
    return template.substitute(substitutions)


def main():
    english = json.loads((ROOT / 'content-en.json').read_text(encoding='utf-8-sig'))
    chinese = json.loads((ROOT / 'content-zh.json').read_text(encoding='utf-8-sig'))
    template = Template((ROOT / 'template.html').read_text(encoding='utf-8'))
    pages = {language: render(data, english, language, template) for language, data in [('en', english), ('zh', chinese)]}
    # Render both editions before writing either page.
    DEST.mkdir(parents=True, exist_ok=True)
    assets = DEST / 'assets'
    assets.mkdir(exist_ok=True)
    for name in ('site.css', 'site.js', 'portrait.jpeg', 'favicon.svg'):
        shutil.copyfile(ROOT / name, assets / name)
    (DEST / 'index.html').write_text(pages['en'], encoding='utf-8')
    (DEST / 'zh').mkdir(exist_ok=True)
    (DEST / 'zh/index.html').write_text(pages['zh'], encoding='utf-8')
    (DEST / '_config.yml').write_text('title: Shiyang Ma\ndescription: Statistical genetics and biostatistics\nauthor: Shiyang Ma\nurl: "https://tienan.github.io"\nbaseurl: "/ma-lab"\n', encoding='utf-8')
    print(json.dumps({'built': True, 'directory': str(DEST), 'languages': ['en', 'zh-CN'], 'pages': ['index.html', 'zh/index.html'], 'publication_count_per_language': len(english['publications']), 'assets': 4}, ensure_ascii=True))


if __name__ == '__main__':
    main()
