#coding=utf-8

import os
import requests
import json
from lxml import etree
from tqdm import tqdm


class HuaweiCloud:
    def __init__(self):
        self.index_url = 'https://support.huaweicloud.com'
        self.sess = requests.Session()
        self.headers = {
            'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
        }

    def get_menu_items(self):
        '''从帮助文档主页获取所有分类以及子目录链接
		'''
        response = self.sess.get(self.index_url, headers=self.headers)
        html = etree.HTML(response.text)
        heading_1 = html.xpath('//*[@class="support-nav"]/ul/li/a/text()')
        heading_1_id = html.xpath(
            '//li[contains(@class,"support-menu-li")]/@id')
        menu_items = {
            h1.strip(): {
                'id': h1_id.strip()
            }
            for h1, h1_id in zip(heading_1, heading_1_id)
        }
        print('正在获取h1和h2')
        for key, val in tqdm(menu_items.items()):
            h1_id = val['id']
            heading_2 = html.xpath('//*[@id="' + h1_id +
                                   '"]/div/ul/li/a/text()')
            heading_2_link = html.xpath('//*[@id="' + h1_id +
                                        '"]/div/ul/li/a/@href')
            val['heading_2'] = [{h2.strip(): {}} for h2 in heading_2]
            val['heading_2_link'] = []
            val['leftmenu_link'] = []
            for link in heading_2_link:
                if link.startswith('http'):
                    val['heading_2_link'].append(link)
                else:
                    val['heading_2_link'].append(self.index_url + link)
            for h2_l in val['heading_2_link']:
                val['leftmenu_link'].append(
                    h2_l.replace('index.html',
                                 'v3_support_leftmenu_fragment.html', 1))

        # 获取所有h2菜单的所有页面信息h3
        print('正在获取h3')
        for h1, h1_val in tqdm(menu_items.items()):
            for i, h2_leftmenu_link in enumerate(h1_val['leftmenu_link']):
                response = self.sess.get(h2_leftmenu_link,
                                         headers=self.headers)
                html = etree.HTML(response.text)
                heading_3 = html.xpath('//li[contains(@class,"nav")]/a/text()')
                heading_3_link = html.xpath(
                    '//li[contains(@class,"nav")]/a/@href')
                for j, link in enumerate(heading_3_link):
                    if link.startswith('javascript'):
                        pass
                    elif not link.startswith('http'):
                        heading_3_link[j] = self.index_url + link
                h2 = h1_val['heading_2'][i]
                h2[list(h2.keys())[0]] = {
                    'heading_3': heading_3,
                    'heading_3_link': heading_3_link
                }

        json_str = json.dumps(menu_items,
                              indent=4,
                              sort_keys=True,
                              ensure_ascii=False)
        with open('menu_items.json', 'w') as f:
            f.write(json_str)
        return menu_items

    def download_page(self,
                      heading_1_list,
                      menu_items_json_path='menu_items.json'):
        '''下载某一个h1下的所有h3页面
		'''
        menu_items = json.load(open(menu_items_json_path))

        for heading_1 in heading_1_list:
            if heading_1 not in menu_items.keys():
                print('heading_1：【{}】不存在！'.format(heading_1))
                return

            h2_content_list = menu_items[heading_1]['heading_2']
            for h2_content in tqdm(h2_content_list):
                for heading_2, val in h2_content.items():
                    print('正在下载页面：{}-{}'.format(heading_1, heading_2))
                    heading_3_list = val['heading_3']
                    heading_3_link_list = val['heading_3_link']
                    for heading_3, heading_3_link in zip(
                            heading_3_list, heading_3_link_list):
                        if not heading_3_link.startswith('javascript'):
                            response = self.sess.get(heading_3_link,
                                                     headers=self.headers)
                            sava_path = os.path.join(heading_1, heading_2)
                            if not os.path.exists(sava_path):
                                os.makedirs(sava_path)
                            sava_path = sava_path + '/' + heading_3.replace(
                                '/', '_') + '.html'
                            with open(sava_path, 'w') as f:
                                f.write(response.text)
            print('heading_1：【{}】所有页面下载完成！'.format(heading_1))

    def clean_list(self, l):
        result = []
        for i in l:
            i = i.strip()
            if (i != '') and (not i.isspace()):
                result.append(i)
        return result

    def extract_title(self, html):
        title = html.xpath('//h1[contains(@class,"topictitle1")]/text()')
        title = ''.join(title)
        result = title.strip()
        return result

    def extract_link(self, html):
        link = html.xpath('//link[@rel="canonical"]/@href')
        result = '/'.join([self.index_url, ''.join(link)])
        return result

    def extract_title_content(self, html):
        # 不同类型
        # 1：p型段落
        # 2：div型段落
        # 3：ul-li型列表
        # 4: ul型段落
        title_content_p = html.xpath(
            '//div[@class="help-content"]/div[contains(@id,"body")]/p//text()')
        title_content_div = html.xpath(
            '//div[@class="help-content"]/div[contains(@id,"body")]/div[@class="p"]//text()'
        )
        title_content_ul_li = html.xpath(
            '//div[@class="help-content"]/div[contains(@id,"body")]/div[@class="p"]/ul/li//text()'
        )
        title_content_ul = html.xpath(
            '//div[@class="help-content"]/div[contains(@id,"body")]/ul//text()'
        )
        # 简单清洗
        title_content_p = self.clean_list(title_content_p)
        title_content_div = self.clean_list(title_content_div)
        title_content_ul_li = self.clean_list(title_content_ul_li)
        title_content_ul = self.clean_list(title_content_ul)

        p_content = '\n'.join(title_content_p)
        div_content = '\n'.join(title_content_div)
        ul_li_content = '\n'.join([
            str(i) + '. ' + j for i, j in zip(
                range(1, len(title_content_ul_li)), title_content_ul_li)
        ])
        title_content_ul = '\n'.join(title_content_ul)
        result = '\n'.join(
            [p_content, div_content, ul_li_content, title_content_ul])
        return result

    def extract_subject(self, html):
        # 方案1：使用subject的页面元素
        # subject = html.xpath('//*[@class="crumbs"]//text()')
        # result = []
        # # 清洗js语句和其它空白字符
        # for s in subject:
        # 	s = s.strip()
        # 	if not s.startswith('var $product') and s != '':
        # 		result.append(s)
        # result = ''.join(result).split('>')

        # 方案2：使用title标签
        subject = html.xpath('//title/text()')
        # 简单清洗
        result = subject[0].replace('_华为云', '')
        result = result.split('_')
        result = self.clean_list(result)
        # 改变顺序
        result.append(result.pop(0))
        return result

    def extract_subtitle(self, html):
        '''
		抽取子标题和子标题
		:param html: DOM页面
		:return:标题
		'''
        subtitle = html.xpath('//*[@class="sectiontitle"]//text()')
        # subtitle = html.xpath('//div[contains(@class,"section")]/h4/text()')
        # 简单清洗
        result = self.clean_list(subtitle)
        # result = subtitle
        return result

    def extract_subcontent(self, html, subtitle):
        subcontent = html.xpath('//div[contains(@id,"body")]/div//text()')
        # t = s.xpath('.//text()')
        if not subcontent:
            subcontent = html.xpath(
                '//div[contains(@id,"section")]/div[contains(@class, "c-div")]//text()'
            )
        # 简单清洗
        # subcontent = ['\n'.join(s.xpath('.//text()')) for s in subcontent_p]
        subcontent = self.clean_list(subcontent)
        result = []
        start_index = 0
        end_index = 0
        # 删除第一个没用的标题
        if subtitle:
            subtitle.pop(0)
            for t in subtitle:
                subcontent_copy = subcontent.copy()
                subcontent_copy.reverse()

                # 检测“请参考。。。”情况
                while True:
                    try:
                        cankao_index = subcontent_copy.index('请参考')
                    except ValueError:
                        break
                    else:
                        subcontent_copy[cankao_index] = '#'
                        subcontent_copy[cankao_index - 1] = '#'

                # 检测表格误判断
                if subcontent_copy.count(t) > 1:
                    while True:
                        try:
                            shuoming_index = subcontent_copy.index('说明')
                        except ValueError:
                            break
                        else:
                            subcontent_copy[shuoming_index] = '#'
                            if subcontent_copy[shuoming_index + 1] == t:
                                subcontent_copy[shuoming_index + 1] = '#'

                # 从后往前计算索引值
                end_index = len(subcontent) - subcontent_copy.index(t) - 1
                result.append('\n'.join(subcontent[start_index + 1:end_index]))
                start_index = end_index
            result.append('\n'.join(subcontent[start_index + 1:]))
        return result

    def parse_page(self, html_list):
        # 用于从存储解析出的内容
        contents = []

        # print('正在解析页面：')
        for file in tqdm(html_list):
            content = {}

            with open(file, 'r') as f:
                html_text = f.read()

            html = etree.HTML(html_text)

            # title
            content['title'] = self.extract_title(html)

            # link
            content['link'] = self.extract_link(html)

            # title_content
            content['title_content'] = self.extract_title_content(html)

            # subject
            content['subject'] = self.extract_subject(html)

            # subtitle
            subtitle = self.extract_subtitle(html)
            content['subtitle'] = subtitle.copy()
            content['subtitle_nums'] = len(subtitle)

            # subcontent
            subcontent = self.extract_subcontent(html, subtitle)
            content['subcontent'] = subcontent

            contents.append(content)
        # print('解析完成，正在写入文件.')
        json_str = json.dumps(contents,
                              indent=4,
                              sort_keys=True,
                              ensure_ascii=False)
        # with open(save_path, 'w') as f:
        #     f.write(json_str)
        # print('写入完毕！')
        return contents