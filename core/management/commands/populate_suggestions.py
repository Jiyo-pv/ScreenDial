from django.core.management.base import BaseCommand
from core.models import CommandSuggestion

class Command(BaseCommand):
    help = 'Populates the CommandSuggestion table with Windows shortcuts and hints'

    def handle(self, *args, **options):
        suggestions = [

# ================= SYSTEM / CORE =================
{'keyword': 'task manager', 'suggestion': 'Ctrl + Shift + Esc', 'description': 'Open Task Manager instantly.'},
{'keyword': 'lock', 'suggestion': 'Win + L', 'description': 'Lock your PC.'},
{'keyword': 'run', 'suggestion': 'Win + R', 'description': 'Open Run dialog.'},
{'keyword': 'settings', 'suggestion': 'Win + I', 'description': 'Open Windows Settings.'},
{'keyword': 'file explorer', 'suggestion': 'Win + E', 'description': 'Open File Explorer.'},
{'keyword': 'search', 'suggestion': 'Win + S', 'description': 'Open Windows Search.'},
{'keyword': 'show desktop', 'suggestion': 'Win + D', 'description': 'Minimize all windows.'},
{'keyword': 'minimize all', 'suggestion': 'Win + M', 'description': 'Minimize all windows.'},
{'keyword': 'restore windows', 'suggestion': 'Win + Shift + M', 'description': 'Restore minimized windows.'},
{'keyword': 'close window', 'suggestion': 'Alt + F4', 'description': 'Close active window.'},
{'keyword': 'switch apps', 'suggestion': 'Alt + Tab', 'description': 'Switch between applications.'},
{'keyword': 'task view', 'suggestion': 'Win + Tab', 'description': 'Open Task View.'},
{'keyword': 'new desktop', 'suggestion': 'Win + Ctrl + D', 'description': 'Create virtual desktop.'},
{'keyword': 'close desktop', 'suggestion': 'Win + Ctrl + F4', 'description': 'Close virtual desktop.'},
{'keyword': 'clipboard history', 'suggestion': 'Win + V', 'description': 'Open Clipboard History.'},
{'keyword': 'emoji panel', 'suggestion': 'Win + .', 'description': 'Open Emoji Picker.'},
{'keyword': 'magnifier', 'suggestion': 'Win + Plus (+)', 'description': 'Zoom screen.'},
{'keyword': 'narrator', 'suggestion': 'Win + Ctrl + Enter', 'description': 'Enable Narrator.'},

# ================= SCREEN / DISPLAY =================
{'keyword': 'screenshot', 'suggestion': 'Win + Shift + S', 'description': 'Open Snipping Tool.'},
{'keyword': 'project display', 'suggestion': 'Win + P', 'description': 'Switch display mode.'},
{'keyword': 'rotate screen', 'suggestion': 'Ctrl + Alt + Arrow', 'description': 'Rotate display orientation.'},
{'keyword': 'fullscreen', 'suggestion': 'F11', 'description': 'Toggle fullscreen mode.'},

# ================= WINDOW MANAGEMENT =================
{'keyword': 'snap left', 'suggestion': 'Win + Left Arrow', 'description': 'Snap window left.'},
{'keyword': 'snap right', 'suggestion': 'Win + Right Arrow', 'description': 'Snap window right.'},
{'keyword': 'maximize window', 'suggestion': 'Win + Up Arrow', 'description': 'Maximize active window.'},
{'keyword': 'minimize window', 'suggestion': 'Win + Down Arrow', 'description': 'Minimize active window.'},
{'keyword': 'move window monitor', 'suggestion': 'Win + Shift + Arrow', 'description': 'Move window across monitors.'},

# ================= TEXT / EDITING =================
{'keyword': 'copy', 'suggestion': 'Ctrl + C', 'description': 'Copy selected item.'},
{'keyword': 'paste', 'suggestion': 'Ctrl + V', 'description': 'Paste item.'},
{'keyword': 'cut', 'suggestion': 'Ctrl + X', 'description': 'Cut selection.'},
{'keyword': 'undo', 'suggestion': 'Ctrl + Z', 'description': 'Undo last action.'},
{'keyword': 'redo', 'suggestion': 'Ctrl + Y', 'description': 'Redo last action.'},
{'keyword': 'select all', 'suggestion': 'Ctrl + A', 'description': 'Select everything.'},
{'keyword': 'save', 'suggestion': 'Ctrl + S', 'description': 'Save file.'},
{'keyword': 'find', 'suggestion': 'Ctrl + F', 'description': 'Find text.'},
{'keyword': 'replace', 'suggestion': 'Ctrl + H', 'description': 'Replace text.'},
{'keyword': 'new document', 'suggestion': 'Ctrl + N', 'description': 'Create new document.'},
{'keyword': 'open file', 'suggestion': 'Ctrl + O', 'description': 'Open file.'},
{'keyword': 'print', 'suggestion': 'Ctrl + P', 'description': 'Print document.'},

# ================= BROWSER =================
{'keyword': 'new tab', 'suggestion': 'Ctrl + T', 'description': 'Open new tab.'},
{'keyword': 'close tab', 'suggestion': 'Ctrl + W', 'description': 'Close tab.'},
{'keyword': 'reopen tab', 'suggestion': 'Ctrl + Shift + T', 'description': 'Reopen closed tab.'},
{'keyword': 'incognito', 'suggestion': 'Ctrl + Shift + N', 'description': 'Open private window.'},
{'keyword': 'downloads', 'suggestion': 'Ctrl + J', 'description': 'Open downloads.'},
{'keyword': 'history', 'suggestion': 'Ctrl + H', 'description': 'Open history.'},
{'keyword': 'refresh page', 'suggestion': 'F5', 'description': 'Refresh page.'},

# ================= TROUBLESHOOTING (VERY IMPORTANT 😎) =================
{'keyword': 'pc frozen', 'suggestion': 'Ctrl + Alt + Delete', 'description': 'Open security options.'},
{'keyword': 'app not responding', 'suggestion': 'Alt + F4', 'description': 'Close frozen application.'},
{'keyword': 'slow computer', 'suggestion': 'Ctrl + Shift + Esc', 'description': 'Check Task Manager.'},
{'keyword': 'force close', 'suggestion': 'Alt + F4', 'description': 'Force close window.'},

# ================= POWER USER =================
{'keyword': 'rename file', 'suggestion': 'F2', 'description': 'Rename selected file.'},
{'keyword': 'delete file', 'suggestion': 'Delete', 'description': 'Move file to Recycle Bin.'},
{'keyword': 'permanent delete', 'suggestion': 'Shift + Delete', 'description': 'Delete permanently.'},
{'keyword': 'new folder', 'suggestion': 'Ctrl + Shift + N', 'description': 'Create new folder.'},
{'keyword': 'properties', 'suggestion': 'Alt + Enter', 'description': 'Open file properties.'},
{'keyword': 'refresh desktop', 'suggestion': 'F5', 'description': 'Refresh desktop.'},

# ================= EXTENDED PRACTICAL COMMANDS =================
{'keyword': 'open explorer', 'suggestion': 'Win + E', 'description': 'Open File Explorer.'},
{'keyword': 'open notifications', 'suggestion': 'Win + N', 'description': 'Open Notification Center.'},
{'keyword': 'quick settings', 'suggestion': 'Win + A', 'description': 'Open Quick Settings.'},
{'keyword': 'voice typing', 'suggestion': 'Win + H', 'description': 'Start dictation.'},
{'keyword': 'game bar', 'suggestion': 'Win + G', 'description': 'Open Xbox Game Bar.'},

]


        created_count = 0
        for item in suggestions:
            obj, created = CommandSuggestion.objects.get_or_create(
                keyword=item['keyword'],
                defaults={'suggestion': item['suggestion'], 'description': item['description']}
            )
            if created:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully added {created_count} shortcuts.'))
