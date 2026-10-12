#!/usr/bin/env python3
"""Create a two-page, Cyrillic-safe Product Masters assignment as PDF and PNG previews."""
from pathlib import Path
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.enums import TA_CENTER
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'submission'
OUT.mkdir(parents=True, exist_ok=True)
FONT_PATHS = [
    ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
    ('/usr/local/share/fonts/DejaVuSans.ttf','/usr/local/share/fonts/DejaVuSans-Bold.ttf'),
]
regular, bold = next(((Path(a), Path(b)) for a,b in FONT_PATHS if Path(a).exists() and Path(b).exists()),(None,None))
if not regular:
    raise RuntimeError('Missing DejaVu Sans fonts. Install fonts-dejavu-core.')
pdfmetrics.registerFont(TTFont('DV', str(regular)))
pdfmetrics.registerFont(TTFont('DV-Bold', str(bold)))
pdfmetrics.registerFontFamily('DV',normal='DV',bold='DV-Bold')
NAVY=colors.HexColor('#10283B')
BLUE=colors.HexColor('#1A6178')
MINT=colors.HexColor('#E4F4F1')
GRAY=colors.HexColor('#5B7180')
LINE=colors.HexColor('#D7E3E8')
WASH=colors.HexColor('#F3F7F8')
ORANGE=colors.HexColor('#B57624')

style={
 'title': ParagraphStyle('title',fontName='DV-Bold',fontSize=20.0,leading=25,textColor=NAVY,spaceAfter=9),
 'subtitle': ParagraphStyle('subtitle',fontName='DV',fontSize=10.4,leading=15,textColor=BLUE,spaceAfter=7),
 'section': ParagraphStyle('section',fontName='DV-Bold',fontSize=11,leading=15,textColor=BLUE,spaceBefore=13,spaceAfter=6,keepWithNext=True),
 'body': ParagraphStyle('body',fontName='DV',fontSize=8.75,leading=13.3,textColor=NAVY,spaceAfter=6),
 'small': ParagraphStyle('small',fontName='DV',fontSize=7.8,leading=11.7,textColor=GRAY,spaceAfter=4),
 'tiny': ParagraphStyle('tiny',fontName='DV',fontSize=7.15,leading=10.8,textColor=NAVY),
 'tablehead': ParagraphStyle('tablehead',fontName='DV-Bold',fontSize=7.5,leading=11.0,textColor=BLUE),
 'metric': ParagraphStyle('metric',fontName='DV-Bold',fontSize=20,leading=25,textColor=NAVY,alignment=TA_CENTER),
 'metriclab': ParagraphStyle('metriclab',fontName='DV',fontSize=7.2,leading=10.3,textColor=GRAY,alignment=TA_CENTER),
}
def P(txt, st='body'):
    return Paragraph(txt,style[st])
def H(txt): return P(txt,'section')
def T(data,widths,head=True,pad=7):
    result=Table([[P(t,'tablehead' if i==0 else 'tiny') for t in row] for i,row in enumerate(data)], colWidths=widths,repeatRows=1 if head else 0,hAlign='LEFT')
    commands=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),pad),('RIGHTPADDING',(0,0),(-1,-1),pad),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,-1),.3,LINE)]
    if head: commands += [('BACKGROUND',(0,0),(-1,0),MINT),('LINEBELOW',(0,0),(-1,0),.7,BLUE),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,WASH])]
    result.setStyle(TableStyle(commands));return result

PAGE_W=A4[0]-74

def footer(canv,doc):
    canv.saveState();w,h=A4
    canv.setStrokeColor(BLUE);canv.setLineWidth(0.9);canv.line(37,h-28,w-37,h-28)
    canv.setFont('DV',7.2);canv.setFillColor(GRAY)
    canv.drawString(37,25,'PRODUCT MASTERS  /  НЕДЕЛЯ 1  /  УРОВЕНЬ 2')
    canv.drawRightString(w-37,25,f'{doc.page} / 2')
    canv.restoreState()

story=[]
story += [P('Как вырастить retention с 15% до 30–35%','title'), P('RFM-стратегия без дополнительного привлечения покупателей · продуктовый кейс','subtitle')]
story += [H('01  /  Диагноз: что известно и что требуется уточнить')]
story += [P('<b>По условию:</b> e-commerce с историей 12 месяцев, <b>600 продаж в день</b>, повторные покупки снижаются два последних месяца, текущий retention <b>15%</b>, привлечение новых пользователей стабильно. Цель — <b>30–35%</b>.')]
story += [P('<b>Первое решение:</b> определить retention одинаково для всех когорт: доля покупателей, совершивших <b>вторую оплаченную покупку в течение 60 дней</b> после первой. Это моя предложенная операционная метрика; прежде чем сравнивать с исходными 15%, необходимо проверить, что в условии использовалось то же определение и окно. Отказы и возвраты исключить.')]

metrics=T([
    ['<b>15%</b><br/>Текущий уровень','<b>30–35%</b><br/>Цель','<b>+15–20 п. п.</b><br/>Нужное изменение'],
], [PAGE_W/3]*3,head=False,pad=11)
story += [metrics,P('600 продаж/день — это <b>заказы, а не уникальные клиенты когорты</b>: умножать 600 на retention и обещать число «возвращённых» покупателей некорректно. Цель соответствует росту показателя в 2,0–2,33 раза, но не является прогнозом.','small')]

story += [H('02  /  Где я буду искать причину падения')]
story += [P('<b>Проверка 1 — когорты:</b> сравнить покупателей с первой покупкой по неделям, фиксируя одинаковый 60-дневный горизонт. Последние когорты включать лишь после полного созревания окна. <b>Проверка 2 — путь после заказа:</b> доля получивших товар вовремя, обращения, возвраты, доставка, повторное посещение и повторная оплата. <b>Проверка 3 — ассортимент:</b> наличие товаров, категории и обычный цикл повторной потребности. Отдельно проверить изменение доли новых покупателей и каналов.')]
story += [P('<b>Ключевая гипотеза:</b> проблема может быть не в привлечении, а в отсутствии своевременного и релевантного повода для второй покупки — либо в ухудшении первого опыта. RFM покажет, <i>кого</i> проверять первым, но не объяснит причину само по себе.','small')]

story += [H('03  /  Как сегментирую через RFM')]
story += [P('<b>R</b> — дни с последнего оплаченного заказа (чем меньше, тем выше балл); <b>F</b> — число заказов за 12 месяцев; <b>M</b> — оплаченная сумма за вычетом возвратов. Для каждого показателя — баллы 1–5 по реальным распределениям; равные значения должны получать одинаковый балл. Пороговые группы ниже — предлагаемые правила, а не рассчитанные доли клиентов.')]
story += [T([
 ['Сегмент','Условие по баллам','Что это означает'],
 ['<b>Champions</b>','R ≥ 4; F ≥ 4; M ≥ 4','Активные, частые и ценные покупатели'],
 ['<b>At Risk</b>','R ≤ 2; F ≥ 3 или M ≥ 4','Раньше покупали активно; давно нет заказа'],
 ['<b>Potential Loyalists</b>','R ≥ 4; F ≤ 3','Купили недавно, ещё не стали регулярными'],
 ['<b>Hibernating</b>','R ≤ 2; F ≤ 2; M ≤ 3','Редко и давно покупают, возврат под вопросом'],
],[PAGE_W*.25,PAGE_W*.28,PAGE_W*.47])]
story += [P('Правила применяются последовательно: Champions → At Risk → Potential Loyalists → Hibernating; прочие комбинации попадают в «Другие». Без истории заказов нельзя утверждать, сколько клиентов оказалось в каждом сегменте.','small')]

story += [PageBreak(), P('От сегментов — к росту повторных покупок','title'),P('Приоритет — вторая покупка и измеримый эффект, а не массовые скидки','subtitle')]
story += [H('04  /  Гипотезы и конкретные действия')]
story += [T([
 ['Сегмент','Что предлагаю сделать','Что должно измениться'],
 ['<b>Potential Loyalists</b><br/>Приоритет №1','После доставки — полезное письмо с уходом / инструкцией; затем персональная подборка дополнений с учётом купленной категории и её цикла. Без скидки на первом шаге.','Растёт доля <b>вторых покупок</b> в течение 60 дней.'],
 ['<b>At Risk</b><br/>Приоритет №2','Сверить причину отсутствия покупок и опыт доставки; затем напомнить подходящий товар или обновление ассортимента. Ограниченное предложение — только после теста маржи.','Растёт доля <b>реактивированных</b> покупателей в фиксированном окне.'],
 ['<b>Champions</b>','Ранний доступ к релевантным новинкам и качественный сервис. Не раздавать скидки тем, кто и так купит.','Сохраняются частота повторных заказов и <b>маржа</b>.'],
 ['<b>Hibernating</b>','Один дешёвый win-back контакт с вопросом об актуальной потребности; неактивных и отказавшихся исключить из дальнейших касаний.','Есть <b>дополнительные</b> покупки при оправданной стоимости возврата.'],
],[PAGE_W*.22,PAGE_W*.49,PAGE_W*.29])]
story += [P('<b>Почему не «дать скидку всем под риском»:</b> максимальный риск ухода не равен максимальной реакции на кампанию. Поэтому тестировать не только вероятность ухода, но и <b>разницу с контрольной группой</b>.','small')]
story += [H('05  /  План: измерить → запустить → масштабировать')]
story += [T([
 ['Этап','Действие и критерий перехода'],
 ['<b>Неделя 1</b>','Проверить определение retention, зрелость 60-дневных когорт, причины возвратов и динамику по каналам и категориям. Зафиксировать чистые заказы и клиентов.'],
 ['<b>Неделя 2</b>','Рассчитать RFM. Запустить два небольших сценария: постпокупочный follow-up для Potential Loyalists и реактивацию At Risk; в каждом сегменте оставить случайный контроль.'],
 ['<b>Далее</b>','После полного окна повторной покупки сравнить uplift по сегментам, валовую маржу за вычетом стимулов/доставки/CRM и жалобы. Масштабировать только выигрышные сценарии.'],
],[PAGE_W*.18,PAGE_W*.82])]
story += [H('06  /  Как пойму, что цель достигнута')]
story += [P('<b>Главная метрика:</b> 60-day second-purchase retention = уникальные покупатели когорты, совершившие второй оплаченный заказ за 60 дней / все покупатели той же созревшей когорты × 100%. <b>Цель:</b> 30–35% против сопоставимых 15%, если исходный показатель действительно рассчитан так же.')]
story += [P('<b>Эксперимент:</b> случайное разделение на коммуникацию и обычный путь внутри каждого сегмента, одинаковые периоды и каналы. <b>Uplift:</b> доля повторных покупателей в тесте минус доля в контроле (п. п.). <b>Защитные показатели:</b> маржа на назначенного клиента, возвраты, жалобы и отписки. Статистическую точность проверить на реальном размере когорты до вывода об эффекте.')]
story += [H('07  /  Решение продуктового менеджера')]
story += [P('Начинаю с <b>Potential Loyalists</b>: своевременный и полезный путь ко второй покупке ближе всего к цели retention. Одновременно проверяю <b>At Risk</b>, но не трачу бюджет на массовые скидки. <b>30–35% — цель, а не гарантированный результат:</b> достижение подтверждается только на созревших когортах и в сравнении с контролем.')]
story += [P('Основа подхода: Fader, Hardie & Lee (2005), RFM/CLV; Ascarza (2018), Retention Futility; Sahni, Zou & Chintagunta (2017), 70 полевых экспериментов. Источники и ограничения проверки: docs/research-notes.md в GitHub.','small')]

def run():
    pdf=OUT/'Product_Masters_RFM_Medium_RU.pdf'
    doc=SimpleDocTemplate(str(pdf),pagesize=A4,leftMargin=37,rightMargin=37,topMargin=42,bottomMargin=43,
      title='RFM: рост удержания с 15 до 30–35 процентов',author='Product Masters — учебный кейс')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    import fitz
    d=fitz.open(pdf)
    if len(d)!=2: raise RuntimeError(f'PDF должен иметь две страницы, получено {len(d)}')
    for i,p in enumerate(d,1):
        p.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False).save(OUT/f'RFM_Medium_Page_{i}.png')
        for box in p.get_text('blocks'):
            if box[0]<0 or box[1]<0 or box[2]>p.rect.width+1 or box[3]>p.rect.height+1:
                raise RuntimeError('PDF text block outside page')
    print(f'OK: {pdf}, {pdf.stat().st_size} bytes, {len(d)} pages')
if __name__=='__main__': run()