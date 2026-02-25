#!/usr/bin/env swift
//
// send-to-desktop.swift
// Activates Claude Desktop, opens a new Cowork task, pastes a prompt, and submits.
// Desktop's CLAUDE.md handles folder context and boot sequence.
//
// Usage:
//   swift bridge/send-to-desktop.swift "Your prompt here"
//   swift bridge/send-to-desktop.swift --file /path/to/prompt.txt
//
// Requires: Accessibility permissions for the swift runtime

import Cocoa
import ApplicationServices

// MARK: - Helpers

func findElement(_ root: AXUIElement, role: String? = nil, description: String? = nil, title: String? = nil, maxDepth: Int = 25, currentDepth: Int = 0) -> AXUIElement? {
    if currentDepth > maxDepth { return nil }

    var elRole: CFTypeRef?
    var elDesc: CFTypeRef?
    var elTitle: CFTypeRef?

    AXUIElementCopyAttributeValue(root, kAXRoleAttribute as CFString, &elRole)
    AXUIElementCopyAttributeValue(root, kAXDescriptionAttribute as CFString, &elDesc)
    AXUIElementCopyAttributeValue(root, kAXTitleAttribute as CFString, &elTitle)

    let r = elRole as? String ?? ""
    let d = elDesc as? String ?? ""
    let t = elTitle as? String ?? ""

    let roleMatch = role == nil || r == role
    let descMatch = description == nil || d == description
    let titleMatch = title == nil || t.contains(title ?? "")

    if roleMatch && descMatch && titleMatch {
        if role != nil || description != nil || title != nil {
            return root
        }
    }

    var children: CFTypeRef?
    AXUIElementCopyAttributeValue(root, kAXChildrenAttribute as CFString, &children)
    if let kids = children as? [AXUIElement] {
        for kid in kids {
            if let found = findElement(kid, role: role, description: description, title: title, maxDepth: maxDepth, currentDepth: currentDepth + 1) {
                return found
            }
        }
    }
    return nil
}

func pressElement(_ element: AXUIElement) -> Bool {
    return AXUIElementPerformAction(element, kAXPressAction as CFString) == .success
}

func focusElement(_ element: AXUIElement) -> Bool {
    return AXUIElementSetAttributeValue(element, kAXFocusedAttribute as CFString, true as CFTypeRef) == .success
}

func retry(_ label: String, attempts: Int = 5, delay: TimeInterval = 1.0, action: () -> Bool) -> Bool {
    for attempt in 1...attempts {
        if action() { return true }
        if attempt < attempts {
            fputs("\(label) not found, retrying (\(attempt)/\(attempts))...\n", stderr)
            Thread.sleep(forTimeInterval: delay)
        }
    }
    return false
}

func sendCommandPeriod() {
    // Use osascript/System Events to reliably target the Claude process
    let script = """
        tell application "System Events"
            tell process "Claude"
                keystroke "." using {command down}
            end tell
        end tell
        """
    let task = Process()
    task.launchPath = "/usr/bin/osascript"
    task.arguments = ["-e", script]
    task.launch()
    task.waitUntilExit()
}

func pasteText(_ text: String) {
    let pasteboard = NSPasteboard.general
    let previous = pasteboard.string(forType: .string)
    pasteboard.clearContents()
    pasteboard.setString(text, forType: .string)

    let source = CGEventSource(stateID: .combinedSessionState)
    // Cmd+V (keycode 9 = 'v')
    let down = CGEvent(keyboardEventSource: source, virtualKey: 9, keyDown: true)
    down?.flags = .maskCommand
    down?.post(tap: .cghidEventTap)
    let up = CGEvent(keyboardEventSource: source, virtualKey: 9, keyDown: false)
    up?.flags = .maskCommand
    up?.post(tap: .cghidEventTap)

    Thread.sleep(forTimeInterval: 0.5)

    // Restore clipboard
    if let prev = previous {
        pasteboard.clearContents()
        pasteboard.setString(prev, forType: .string)
    }
}

// MARK: - Argument parsing

var prompt: String

if CommandLine.arguments.count < 2 {
    fputs("Usage: swift send-to-desktop.swift \"prompt text\"\n", stderr)
    fputs("       swift send-to-desktop.swift --file /path/to/prompt.txt\n", stderr)
    exit(1)
}

if CommandLine.arguments[1] == "--file" {
    guard CommandLine.arguments.count >= 3 else {
        fputs("Error: --file requires a path argument\n", stderr)
        exit(1)
    }
    let path = CommandLine.arguments[2]
    guard let content = try? String(contentsOfFile: path, encoding: .utf8) else {
        fputs("Error: Could not read file at \(path)\n", stderr)
        exit(1)
    }
    prompt = content.trimmingCharacters(in: .whitespacesAndNewlines)
} else {
    prompt = CommandLine.arguments.dropFirst().joined(separator: " ")
}

// MARK: - Check accessibility

guard AXIsProcessTrusted() else {
    fputs("Error: No accessibility permissions. Grant in System Settings > Privacy & Security > Accessibility.\n", stderr)
    exit(1)
}

// MARK: - Find and activate Claude

let runningApps = NSWorkspace.shared.runningApplications.filter { $0.bundleIdentifier == "com.anthropic.claudefordesktop" }

if runningApps.isEmpty {
    fputs("Launching Claude Desktop...\n", stderr)
    if let appURL = NSWorkspace.shared.urlForApplication(withBundleIdentifier: "com.anthropic.claudefordesktop") {
        let config = NSWorkspace.OpenConfiguration()
        let semaphore = DispatchSemaphore(value: 0)
        NSWorkspace.shared.openApplication(at: appURL, configuration: config) { _, _ in semaphore.signal() }
        semaphore.wait()
    }
    Thread.sleep(forTimeInterval: 3.0)
}

guard let app = NSWorkspace.shared.runningApplications.first(where: { $0.bundleIdentifier == "com.anthropic.claudefordesktop" }) else {
    fputs("Error: Could not find Claude Desktop.\n", stderr)
    exit(1)
}

app.activate()
Thread.sleep(forTimeInterval: 1.0)

let pid = app.processIdentifier
let appRef = AXUIElementCreateApplication(pid)

var windowsValue: CFTypeRef?
AXUIElementCopyAttributeValue(appRef, kAXWindowsAttribute as CFString, &windowsValue)
guard let windows = windowsValue as? [AXUIElement], let window = windows.first else {
    fputs("Error: No Claude windows found.\n", stderr)
    exit(1)
}

// MARK: - Step 1: Switch to Cowork tab

guard retry("Cowork tab", attempts: 3, delay: 0.5, action: {
    if let tab = findElement(window, role: "AXRadioButton", description: "Cowork") {
        fputs("Clicking Cowork tab...\n", stderr)
        _ = pressElement(tab)
        Thread.sleep(forTimeInterval: 1.5)
        return true
    }
    return false
}) else {
    fputs("Error: Could not find Cowork tab.\n", stderr)
    exit(1)
}

// MARK: - Step 2: Click "New task"

var foundNewTask = retry("New task link", attempts: 5, action: {
    if let link = findElement(window, role: "AXLink", description: "New task") {
        fputs("Starting new task...\n", stderr)
        _ = pressElement(link)
        Thread.sleep(forTimeInterval: 1.5)
        return true
    }
    return false
})

if !foundNewTask {
    fputs("Tray may be closed — sending Command-. to toggle...\n", stderr)
    sendCommandPeriod()
    Thread.sleep(forTimeInterval: 1.0)
    foundNewTask = retry("New task link (after toggle)", attempts: 5, action: {
        if let link = findElement(window, role: "AXLink", description: "New task") {
            fputs("Starting new task...\n", stderr)
            _ = pressElement(link)
            Thread.sleep(forTimeInterval: 1.5)
            return true
        }
        return false
    })
}

guard foundNewTask else {
    fputs("Error: Could not find 'New task' link.\n", stderr)
    exit(1)
}

// MARK: - Step 3: Paste prompt into text area

guard retry("Text area", attempts: 5, action: {
    findElement(window, role: "AXTextArea", description: "Write your prompt to Claude") != nil
}) else {
    fputs("Error: Could not find text input area.\n", stderr)
    exit(1)
}

if let textArea = findElement(window, role: "AXTextArea", description: "Write your prompt to Claude") {
    fputs("Pasting prompt...\n", stderr)
    _ = focusElement(textArea)
    Thread.sleep(forTimeInterval: 0.3)
    pasteText(prompt)
    Thread.sleep(forTimeInterval: 0.5)
}

// MARK: - Step 4: Click "Start task" button

guard retry("Start task button", attempts: 5, delay: 0.5, action: {
    if let button = findElement(window, role: "AXButton", description: "Start task") {
        fputs("Clicking Start task...\n", stderr)
        _ = pressElement(button)
        return true
    }
    return false
}) else {
    fputs("Error: Could not find 'Start task' button. Prompt is pasted - submit manually.\n", stderr)
    exit(1)
}

Thread.sleep(forTimeInterval: 0.3)
print("OK: New Cowork task started in Desktop")
