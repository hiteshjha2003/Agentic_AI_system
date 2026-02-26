import * as vscode from 'vscode';
import { getWebviewContent } from './webviewContent';

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('sambanova.openAgent', () => {
      const panel = vscode.window.createWebviewPanel(
        'sambanovaAgent',
        'SambaNova Code Agent (stlite)',
        vscode.ViewColumn.Beside,
        {
          enableScripts: true,
          retainContextWhenHidden: true
        }
      );

      panel.webview.html = getWebviewContent(context.extensionUri);

      // Optional: pass current selection to webview
      const editor = vscode.window.activeTextEditor;
      if (editor) {
        const selection = editor.document.getText(editor.selection);
        panel.webview.postMessage({
          command: 'setSelection',
          code: selection
        });
      }
    })
  );
}