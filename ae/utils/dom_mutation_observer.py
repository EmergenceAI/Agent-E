
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
                        let visibility=node.offsetWidth > 0 && node.offsetHeight > 0;  
                        let content = node.innerText.trim();
                        if(visibility && node.innerText.trim() && window.getComputedStyle(node).display !== 'none'){
                            if(content && !changes_detected.some(change => change.content.includes(content))) {
                                changes_detected.push({tag: node.tagName, content: content});
                            }
                        }                    
                    }
                }
            }
            /*
            else if (mutation.type === 'attributes' && (mutation.attributeName === 'style' || mutation.attributeName === 'class' || mutation.attributeName === 'hidden')) {
                    
                    const targetElement = mutation.target;
                    let oldDisplayStyle;
                    console.log('Mutation:', mutation);
                    if (mutation.attributeName === 'style') {
                        oldDisplayStyle = mutation.oldValue;
                        console.log("Style attribute changed from ", mutation.oldValue, " to ", mutation.target.style.cssText);
                    }
                    else if (mutation.attributeName === 'class') {
                        console.log('Class attribute changed from ', mutation.oldValue, ' to ', targetElement.className);
                         // Create a new element, apply the old class to it, and check its computed style
                        let oldElement = document.createElement(targetElement.tagName);
                        oldElement.className = mutation.oldValue;
                        document.body.appendChild(oldElement); // Temporarily add the element to the document
                        oldDisplayStyle = window.getComputedStyle(oldElement).display;
                        document.body.removeChild(oldElement); // Immediately remove the element
                        console.log('Old display style:', oldDisplayStyle);
                    }
                    
                    const displayStyle = window.getComputedStyle(targetElement).display;
                        console.log('New display style:', displayStyle);
                    if (oldDisplayStyle !== displayStyle) {
                            if (displayStyle !== 'none' && oldDisplayStyle === 'none' ) {
                                console.log('Element is now visible:', targetElement.innerText);
                            } else {
                                console.log('Element is now hidden:', targetElement.innerText);
                            }
                        console.log('Old display style:', oldDisplayStyle);
                        
                    }
                }*/
            } 
        if(changes_detected.length > 0) {
            window.dom_mutation_change_detected(JSON.stringify(changes_detected));
        } 
    }).observe(document, {subtree: true, childList: true}); 
    """)


async def handle_navigation_for_mutation_observer(page:Page):
    await add_mutation_observer(page)

async def dom_mutation_change_detected(changes_detected: str):
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