# VS Code Profiles Setup (Lightweight Extension Isolation)

This guide explains how to isolate project-specific extensions to **run exclusively within this workspace** without polluting other projects and **without consuming additional system resources** (unlike Docker or virtual machines).

---

## Why Use Profiles Instead of Global Installation?

- **Zero extra CPU/RAM overhead:** Operates 100% natively inside VS Code.
- **True workspace isolation:** Other projects will not load or execute workspace-specific extensions, keeping your editor fast and lean.
- **Faster startup times:** Loading only the 4 to 5 required extensions allows the editor to start in milliseconds.

---

## Step-by-Step Setup

### Step 1: Create a Clean Profile

1. In VS Code, open the Command Palette by pressing `Cmd + Shift + P` (macOS) or `Ctrl + Shift + P` (Windows/Linux).
2. Type and select:
   ```text
   Profiles: Create Profile...
   ```
3. Enter a descriptive profile name, for example:
   ```text
   AI Starter
   ```
4. When prompted:
   > *Select a template to use or create from an empty profile*  
   
   Select **`None (Empty Profile)`**.  
   This creates a completely clean profile with no active extensions or inherited configurations.

---

### Step 2: Install Recommended Extensions

1. With the project open in the new profile, open the Extensions view using `Cmd + Shift + X`.
2. Locate the **Workspace Recommendations** section (configured in `.vscode/extensions.json`).
3. Click the install button (or cloud download icon) to install the extensions required for this project:
   - **Live Server** (`ritwickdey.liveserver`)
   - **Prettier - Code formatter** (`esbenp.prettier-vscode`)
   - **ESLint** (`dbaeumer.vscode-eslint`)

> [!NOTE]
> These extensions remain tied exclusively to the `AI Starter` profile.

---

### Step 3: Associate the Profile with This Workspace (Automatic)

To ensure VS Code automatically switches to this profile whenever you open this directory:

1. Press `Cmd + Shift + P`.
2. Type and select:
   ```text
   Profiles: Associate Profile with Workspace...
   ```
3. Select your created profile: **`AI Starter`**.

From this point forward:
- Opening this workspace activates the **AI Starter** profile automatically.
- Opening any other project restores your default profile and its usual extensions.
