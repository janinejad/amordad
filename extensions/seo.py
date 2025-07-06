from bs4 import BeautifulSoup
from django.template.loader import render_to_string


def generate_toc(html_content):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    # Find all heading elements (h1 to h6) using BeautifulSoup's find_all method
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    # Create a list to store the table of contents
    toc = []
    for heading in headings:
        # Get the text and ID (if available) of each heading
        heading_text = heading.get_text(strip=True)
        heading_id = heading.get('id')  # If your headings have IDs
        # Append the heading text and ID to the table of contents list
        toc.append({
            'text': heading_text,
            'id': heading_id
        })

    return toc


def remove_link(content):
    soup = BeautifulSoup(content, 'html.parser')
    a_tags = soup.find_all('a')
    for tag in a_tags:
        tag.replace_with(tag.get_text(strip=True))
    updated_content = soup.prettify()
    return updated_content


def create_link_in_content(specific_text, content, url, authorized_tags_list):
    soup = BeautifulSoup(content, 'html.parser')
    for authorized_tag in authorized_tags_list:
        tags = soup.find_all(authorized_tag)
        tag_num = 0
        for tag in tags:
            # if specific_text in tag.get_text() and tag.find_parent().name not in ['th', 'hd']:
            if specific_text in tag.get_text():
                if tag_num == 0:
                    convert_specific_text_to_link = f'<a href="{url}">{specific_text}</a>'
                    tag.replace_with(
                        BeautifulSoup(str(tag).replace(specific_text, convert_specific_text_to_link, 1),
                                      'html.parser'))
                    tag_num = tag_num + 1
                    break
            if tag_num > 0:
                break
    a_tags = soup.find_all('a')
    for a_tag in a_tags:
        if a_tag.parent.name == "a":
            if a_tag.name == "a":
                a_tag.parent['href'] = a_tag['href']
                a_tag.unwrap()

    updated_context = soup.prettify()
    return updated_context


def get_suggestion_html(object,template_name):
    html = render_to_string(template_name=template_name, context={'object': object})
    return html


def create_contact_form(content):
    import re
    soup = BeautifulSoup(content, "html.parser")
    p_tags = soup.find_all(string=re.compile(r'\[.*?\]'))
    from pages.models import ContactUs
    for p in p_tags:
        lst = re.findall(r'\[(.*?)\]', p.get_text())
        sub_lst = [int(id) for id in lst[0].strip("'").split(",")]
        products = ContactUs.objects.filter(sl=sub_lst)
        divs = get_suggestion_html(products)
        p.replace_with(
            BeautifulSoup(str(p).replace(f"[{lst[0]}]", divs),
                          'html.parser'))
    updated_context = soup.prettify()
    return updated_context
