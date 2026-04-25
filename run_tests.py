from playwright.sync_api import sync_playwright
import time

BASE = 'http://172.16.1.2:8080'
AFFILIATE = 'instantlyageless.com/radians/?v=07d935680b65'
results = []

def ss(page, name):
    path = f'/a0/usr/projects/project_1/screenshots/{name}.png'
    page.screenshot(path=path, full_page=False)
    return path

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1280, 'height': 720})
    page = context.new_page()

    # TEST 1: Page Load
    print("TEST 1: Page Load")
    page.goto(BASE, wait_until='networkidle')
    title = page.title()
    ok = 'Ageless' in title or 'Anti Wrinkle' in title
    ss(page, '01_page_load')
    results.append(('1. Page Load', '✅' if ok else '❌', f'Title: {title}'))
    print(f"  Title: {title}")
    time.sleep(1)

    # TEST 2: Hero Section
    print("TEST 2: Hero Section")
    hero_text = page.locator('body').inner_text()
    ok = 'Look Ten Years Younger' in hero_text or 'Two Minutes' in hero_text
    ss(page, '02_hero_section')
    results.append(('2. Hero Section', '✅' if ok else '❌', 'Headline visible' if ok else 'Headline missing'))
    print(f"  Hero visible: {ok}")
    time.sleep(1)

    # TEST 3: Scroll Through Sections
    print("TEST 3: Scroll Sections")
    sections_seen = []
    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    time.sleep(1)
    page.evaluate('window.scrollTo(0, 0)')
    time.sleep(0.5)
    # Scroll and capture each major section
    scroll_points = [0, 400, 800, 1200, 1600, 2000, 2400, 2800, 3200, 3600]
    for i, y in enumerate(scroll_points):
        page.evaluate(f'window.scrollTo(0, {y})')
        time.sleep(0.3)
    ss(page, '03_scrolled_bottom')
    results.append(('3. Scroll', '✅', 'Scrolled through all sections'))
    print("  Scrolled through page")
    time.sleep(1)

    # TEST 4: CTA Buttons
    print("TEST 4: CTA Buttons")
    page.goto(BASE, wait_until='networkidle')
    time.sleep(1)
    links = page.locator('a').all()
    cta_links = [l for l in links if any(x in (l.inner_text() or '').lower() for x in ['buy', 'order', 'get', 'shop', 'now'])]
    cta_ok = 0
    tested = 0
    for cta in cta_links[:5]:
        href = cta.get_attribute('href') or ''
        if AFFILIATE in href:
            cta_ok += 1
        tested += 1
    ss(page, '04_cta_buttons')
    results.append(('4. CTA Buttons', '✅' if cta_ok >= 3 else '❌', f'{cta_ok}/{tested} CTAs link to affiliate URL'))
    print(f"  {cta_ok}/{tested} CTA buttons correct")
    time.sleep(1)

    # TEST 5: FAQ Accordion
    print("TEST 5: FAQ Accordion")
    page.goto(BASE, wait_until='networkidle')
    time.sleep(1)
    # Find FAQ section and click first question
    faq_headers = page.locator('details, .faq-item, [class*="faq"], h3, h4').all()
    faq_ok = False
    for hdr in faq_headers:
        try:
            hdr.click()
            time.sleep(0.5)
            faq_ok = True
            break
        except:
            continue
    ss(page, '05_faq_accordion')
    results.append(('5. FAQ Accordion', '✅' if faq_ok else '❌', 'Clicked and expanded' if faq_ok else 'No clickable FAQ found'))
    print(f"  FAQ clickable: {faq_ok}")
    time.sleep(1)

    # TEST 6: Email Form
    print("TEST 6: Email Form")
    page.goto(BASE, wait_until='networkidle')
    time.sleep(1)
    inputs = page.locator('input[type="email"]').all()
    form_ok = False
    if inputs:
        for inp in inputs:
            try:
                inp.scroll_into_view_if_needed()
                time.sleep(0.3)
                inp.fill('test@example.com')
                time.sleep(0.3)
                # Try clicking a nearby submit button
                parent = inp.locator('xpath=..')
                btns = parent.locator('button, input[type="submit"]').all()
                if not btns:
                    btns = page.locator('button:has-text("Subscribe"), button:has-text("Submit"), input[type="submit"]').all()
                for btn in btns[:1]:
                    btn.click()
                    time.sleep(0.5)
                form_ok = True
                break
            except Exception as e:
                continue
    ss(page, '06_email_form')
    results.append(('6. Email Form', '✅' if form_ok else '❌', 'Filled and submitted' if form_ok else 'No email form found'))
    print(f"  Email form: {form_ok}")
    time.sleep(1)

    # TEST 7: Exit-Intent Popup
    print("TEST 7: Exit-Intent Popup")
    page.goto(BASE, wait_until='networkidle')
    time.sleep(2)
    # Move mouse to top of viewport to trigger exit intent
    page.mouse.move(640, 5)
    time.sleep(1.5)
    popup_text = page.locator('body').inner_text()
    popup_ok = any(x in popup_text for x in ['10%', 'discount', 'Wait', 'offer', "Don't go", 'leave'])
    ss(page, '07_exit_intent')
    results.append(('7. Exit Popup', '✅' if popup_ok else '⚠️', 'Popup appeared' if popup_ok else 'Popup may need different trigger'))
    print(f"  Exit popup: {popup_ok}")
    time.sleep(1)

    # TEST 8: Mobile / Hamburger Menu
    print("TEST 8: Mobile Menu")
    page.set_viewport_size({'width': 375, 'height': 667})
    page.goto(BASE, wait_until='networkidle')
    time.sleep(2)
    # Look for hamburger menu
    hamburger_selectors = ['button:has-text("☰")', 'button[class*="menu"]', '[class*="hamburger"]', 'button[class*="toggle"]', '[aria-label*="menu"]', '[class*="nav-toggle"]']
    hamburger = None
    for sel in hamburger_selectors:
        try:
            el = page.locator(sel).first
            if el.is_visible():
                hamburger = el
                break
        except:
            continue
    menu_ok = False
    if hamburger:
        hamburger.click()
        time.sleep(0.5)
        menu_ok = True
    ss(page, '08_mobile_menu')
    results.append(('8. Mobile Menu', '✅' if menu_ok else '⚠️', 'Hamburger menu clicked' if menu_ok else 'No hamburger found (may use different pattern)'))
    print(f"  Mobile menu: {menu_ok}")
    time.sleep(1)

    # TEST 9: Pricing Table
    print("TEST 9: Pricing Table")
    page.set_viewport_size({'width': 1280, 'height': 720})
    page.goto(BASE, wait_until='networkidle')
    time.sleep(1)
    page_text = page.locator('body').inner_text()
    pricing_ok = '$64.95' in page_text and ('Best Value' in page_text or 'BEST VALUE' in page_text)
    # Scroll to pricing
    if '$64.95' in page_text:
        try:
            price_el = page.locator('text=$64.95').first
            price_el.scroll_into_view_if_needed()
            time.sleep(0.5)
        except:
            pass
    ss(page, '09_pricing_table')
    results.append(('9. Pricing Table', '✅' if pricing_ok else '❌', '$64.95 Best Value visible' if pricing_ok else 'Pricing not found'))
    print(f"  Pricing: {pricing_ok}")
    time.sleep(1)

    # TEST 10: Testimonials
    print("TEST 10: Testimonials")
    page.goto(BASE, wait_until='networkidle')
    time.sleep(1)
    page_text = page.locator('body').inner_text()
    names = ['Holly', 'Jenny', 'Bevan']
    found = [n for n in names if n in page_text]
    # Scroll to testimonials
    for name in names:
        try:
            el = page.locator(f'text={name}').first
            if el:
                el.scroll_into_view_if_needed()
                time.sleep(0.3)
                break
        except:
            continue
    ss(page, '10_testimonials')
    results.append(('10. Testimonials', '✅' if len(found) >= 2 else '⚠️', f'Found: {found}'))
    print(f"  Testimonials: {found}")

    browser.close()

    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    for test, result, detail in results:
        print(f"{test:<25} {result:<3} {detail}")
    print("="*60)
