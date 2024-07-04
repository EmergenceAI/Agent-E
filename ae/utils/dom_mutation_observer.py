
import asyncio
import json
from typing import Callable  # noqa: UP035

from playwright.async_api import Page

# Create an event loop
loop = asyncio.get_event_loop()

DOM_change_callback: list[Callable[[str], None]] = []

def subscribe(callback: Callable[[str], None]) -> None:
    DOM_change_callback.append(callback)

def unsubscribe(callback: Callable[[str], None]) -> None:
    DOM_change_callback.remove(callback)


async def add_mutation_observer(page:Page):
    """
    Adds a mutation observer to the page to detect changes in the DOM.
    When changes are detected, the observer calls the dom_mutation_change_detected function in the browser context.
    This changes can be detected by subscribing to the dom_mutation_change_detected function by individual skills.

    Current implementation only detects when a new node is added to the DOM.
    However, in many cases, the change could be a change in the style or class of an existing node (e.g. toggle visibility of a hidden node).
    """

    await page.evaluate("""
        console.log('Adding a mutation observer for DOM changes');
        new MutationObserver((mutationsList, observer) => {
            let changes_detected = [];
            for(let mutation of mutationsList) {
                if (mutation.type === 'childList') {
                    let allAddedNodes=mutation.addedNodes;
                    for(let node of allAddedNodes) {
                        if(node.tagName && !['SCRIPT', 'NOSCRIPT', 'STYLE'].includes(node.tagName) && !node.closest('#agentDriveAutoOverlay')) {
                            let visibility=true;
                            let content = node.innerText.trim();
                            if(visibility && node.innerText.trim()){
                                if(content) {
                                    changes_detected.push({tag: node.tagName, content: content});
                                }
                            }
                        }
                    }
                } else if (mutation.type === 'characterData') {
                    let node = mutation.target;
                    if(node.parentNode && !['SCRIPT', 'NOSCRIPT', 'STYLE'].includes(node.parentNode.tagName) && !node.parentNode.closest('#agentDriveAutoOverlay')) {
                        let visibility=true;
                        let content = node.data.trim();
                        if(visibility && content && window.getComputedStyle(node.parentNode).display !== 'none'){
                            if(content && !changes_detected.some(change => change.content.includes(content))) {
                                changes_detected.push({tag: node.parentNode.tagName, content: content});
                            }
                        }
                    }
                }
            }
            if(changes_detected.length > 0) {
                window.dom_mutation_change_detected(JSON.stringify(changes_detected));
            }
        }).observe(document, {subtree: true, childList: true, characterData: true});
        """)


async def handle_navigation_for_mutation_observer(page:Page):
    await add_mutation_observer(page)

async def dom_mutation_change_detected(changes_detected: str):
    """
    Detects changes in the DOM (new nodes added) and emits the event to all subscribed callbacks.
    The changes_detected is a string in JSON formatt containing the tag and content of the new nodes added to the DOM.

    e.g.  The following will be detected when autocomplete recommendations show up when one types Nelson Mandela on google search
    [{'tag': 'SPAN', 'content': 'nelson mandela wikipedia'}, {'tag': 'SPAN', 'content': 'nelson mandela movies'}]
    """
    changes_detected = json.loads(changes_detected.replace('\t', '').replace('\n', ''))
    if len(changes_detected) > 0:
        # Emit the event to all subscribed callbacks
        for callback in DOM_change_callback:
            # If the callback is a coroutine function
            if asyncio.iscoroutinefunction(callback):
                await callback(changes_detected)
            # If the callback is a regular function
            else:
                callback(changes_detected)
