
import json
from playwright.async_api import Page
from typing import List, Callable, Any
from playwright.async_api import Page
import asyncio

# Create an event loop
loop = asyncio.get_event_loop()

DOM_change_callback:List[Any] = []

def subscribe(callback: Callable): # type: ignore
    DOM_change_callback.append(callback) 

def unsubscribe(callback: Callable): # type: ignore
    DOM_change_callback.remove(callback)


async def add_mutation_observer(page:Page):
    print(">>> Added Mutation Observer to the page")
    await page.evaluate(""" 
        console.log('Adding a mutation observer for DOM changes')
        new MutationObserver(async (mutationsList, observer) => {
            let changes_detected = []
            for(let mutation of mutationsList) {
                if (mutation.type === 'childList') {
                    for(let node of mutation.addedNodes) {
                        if(node.tagName && node.tagName !== 'SCRIPT' && node.innerText.trim() && window.getComputedStyle(node).display !== 'none' && !node.closest('#agentDriveAutoOverlay')) {
                            changes_detected.push({tag: node.tagName, content: node.innerText.trim()});
                        }
                    }
                    for(let node of mutation.removedNodes) {
                        if(node.tagName && node.innerText.trim() && window.getComputedStyle(node).display !== 'none') {
                            //do nothing with removed nodes
                        }
                    }
                }
            }
            if(changes_detected.length > 0) {
                window.dom_mutation_change_detected(JSON.stringify(changes_detected));
            } 
        }).observe(document, { childList: true, subtree: true });
    """)

async def handle_navigation_for_mutation_observer(page:Page):
    print(">>> Handling navigation for mutation observer started")
    await add_mutation_observer(page)

async def dom_mutation_change_detected(changes_detected: str):
    changes_detected = json.loads(changes_detected.replace('\t', '').replace('\n', ''))
    if len(changes_detected) > 0:
        print(f"DOM changes detected: {changes_detected}")
        # Emit the event to all subscribed callbacks
        for callback in DOM_change_callback:
            # If the callback is a coroutine function
            if asyncio.iscoroutinefunction(callback):
                await callback(changes_detected)
            # If the callback is a regular function
            else:
                callback(changes_detected)