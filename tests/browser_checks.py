"""Real-browser regression checks; run against the documented local server."""
import os
from urllib.parse import unquote
from playwright.sync_api import sync_playwright, expect

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'))
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto('http://127.0.0.1:8000/')
    expect(page.locator('#group-count')).to_have_value('8')
    page.locator('#start').click()
    expect(page.locator('.group-column')).to_have_count(8)
    expect(page.locator('.item-slot')).to_have_count(24)
    for group in range(8):
        page.locator('.group-name').nth(group).click()
        choices = page.locator('.item-choice')
        expect(choices).to_have_count(10)
        choices.nth(0).click()
        choices.nth(1).click()
        choices.nth(2).click()
        expect(page.locator('#selection-count')).to_have_text('3/3')
        expect(choices.nth(3)).to_be_disabled()
        choices.nth(1).click()
        expect(choices.nth(3)).to_be_enabled()
        choices.nth(3).click()
        if group == 0:
            assert page.locator('#item-dialog').evaluate('(e) => e.scrollHeight <= e.clientHeight')
            page.screenshot(path='/tmp/survival-modal.png')
        page.locator('#confirm').click()
    labels = page.locator('.group-column').first.locator('.item-label')
    assert labels.all_text_contents() == ['Fishing rod', 'Rope (20 metres)', 'Cooking pot']
    page.wait_for_function('Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth && document.documentElement.scrollHeight <= innerHeight')
    assert page.locator('.item-slot').evaluate_all('(els) => els.every(e => {const r=e.getBoundingClientRect(); return r.top>=0 && r.bottom<=innerHeight && r.left>=0 && r.right<=innerWidth})')
    heights = page.locator('.group-column').first.locator('.item-slot').evaluate_all('(els) => els.map(e => e.getBoundingClientRect().height)')
    assert max(heights) - min(heights) < 1
    page.screenshot(path='/tmp/survival-groups.png')
    page.reload()
    expect(page.locator('.group-column')).to_have_count(8)
    assert page.locator('.group-column').first.locator('.item-label').all_text_contents() == ['Fishing rod', 'Rope (20 metres)', 'Cooking pot']
    page.locator('.group-name').first.click()
    expect(page.locator('.item-choice[aria-pressed="true"]')).to_have_count(3)
    page.locator('.item-choice').first.click()
    page.keyboard.press('Escape')
    expect(page.locator('#item-dialog')).not_to_be_visible()
    expect(page.locator('.group-column').first.locator('.item-label')).to_have_count(3)
    page.locator('.group-name').first.click()
    page.locator('.item-choice').first.click()
    page.locator('#close-dialog').click()
    expect(page.locator('.group-column').first.locator('.item-label')).to_have_count(3)
    page.locator('.group-name').first.click()
    while page.locator('.item-choice[aria-pressed="true"]').count():
        page.locator('.item-choice[aria-pressed="true"]').first.click()
    page.locator('#confirm').click()
    expect(page.locator('.group-column').first.locator('.item-label')).to_have_count(0)
    page.locator('#back').click()
    expect(page.locator('#continue')).to_be_visible()
    page.once('dialog', lambda dialog: dialog.dismiss())
    page.locator('#start').click()
    expect(page.locator('#start-screen')).to_be_visible()
    page.locator('#continue').click()
    expect(page.locator('.group-column')).to_have_count(8)
    for count in range(1, 9):
        page.locator('#back').click()
        page.locator('#group-count').select_option(str(count))
        page.once('dialog', lambda dialog: dialog.accept())
        page.locator('#start').click()
        expect(page.locator('.group-column')).to_have_count(count)
        expect(page.locator('#group-table .item-label')).to_have_count(0)
    # Check the longest labels in all 24 slots at projection resolution.
    for group in range(8):
        page.locator('.group-name').nth(group).click()
        for item in [5, 7, 9]:
            page.locator('.item-choice').nth(item).click()
        page.locator('#confirm').click()
    page.wait_for_function('Array.from(document.querySelectorAll("#group-table img")).every(i => i.complete && i.naturalWidth > 0)')
    assert page.locator('#group-table .item-label').evaluate_all('(els) => els.every(e => { const r=e.getBoundingClientRect(); const s=e.parentElement.getBoundingClientRect(); return r.bottom<=s.bottom && r.top>=s.top && r.left>=s.left && r.right<=s.right && r.bottom<=innerHeight })')
    assert page.evaluate('document.documentElement.scrollHeight <= innerHeight && document.documentElement.scrollWidth <= innerWidth')
    # Relative asset URLs must retain a GitHub Pages repository prefix.
    page.route('**/survival/**', lambda route: route.fulfill(path=os.path.join(os.path.dirname(__file__), '..', unquote(route.request.url.split('/survival/', 1)[1].split('?')[0]) or 'index.html')))
    page.goto('http://127.0.0.1:8000/survival/')
    page.locator('.group-name').first.click()
    page.wait_for_function('Array.from(document.querySelectorAll(".item-choice img")).every(i => i.complete && i.naturalWidth > 0)')
    assert page.locator('.item-choice img').first.get_attribute('src') == 'media/rod.jpeg'
    page.keyboard.press('Escape')
    page.set_viewport_size({"width": 390, "height": 844})
    page.locator('.group-name').first.click()
    while page.locator('.item-choice[aria-pressed="true"]').count():
        page.locator('.item-choice[aria-pressed="true"]').first.click()
    page.locator('.item-choice').first.click()
    page.locator('#confirm').click()
    expect(page.locator('.group-column').first.locator('.item-label')).to_have_text('Fishing rod')
    # Focus the heading with the keyboard and open the dialog using Enter.
    page.locator('.group-name').first.focus()
    page.keyboard.press('Enter')
    expect(page.locator('#item-dialog')).to_be_visible()
    page.keyboard.press('Escape')
    assert not errors, errors
    browser.close()
    print('PASS: groups 1–8, selection/order/limits, cancel/edit/clear, storage, reset, all images, 1920×1080 layout, repository paths, mobile and keyboard.')
