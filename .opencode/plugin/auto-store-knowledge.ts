/**
 * Auto-Store Knowledge Plugin
 * 
 * Provides a command to toggle automatic knowledge storage.
 * When enabled, the agent will proactively store technical information.
 * 
 * Commands:
 * - /toggle-auto-store: Enable/disable automatic knowledge storage
 * - /auto-store-status: Check if auto-storage is enabled
 */

export const AutoStoreKnowledge = async ({ project, client, $, directory, worktree }) => {
  // Read configuration state from a local file
  const configFile = `${directory}/.opencode/.auto-store-enabled`;
  
  async function isEnabled() {
    try {
      const result = await $`test -f ${configFile} && cat ${configFile}`.text();
      return result.trim() === 'true';
    } catch {
      return false; // Default to disabled
    }
  }
  
  async function setEnabled(enabled) {
    if (enabled) {
      await $`echo 'true' > ${configFile}`;
    } else {
      await $`echo 'false' > ${configFile}`;
    }
  }

  return {
    /**
     * Handle custom commands
     */
    "tui.command.execute": async (input, output) => {
      if (input.command === "/toggle-auto-store") {
        const currentState = await isEnabled();
        const newState = !currentState;
        await setEnabled(newState);
        
        console.log(`🔄 Auto-store knowledge: ${newState ? '✅ ENABLED' : '❌ DISABLED'}`);
        
        if (newState) {
          console.log('📝 I will now automatically store important technical information.');
          console.log('💡 Use "/toggle-auto-store" again to disable.');
        } else {
          console.log('📝 Automatic storage is now disabled.');
          console.log('💡 You can still manually store with "/store-knowledge"');
        }
      }
      
      if (input.command === "/auto-store-status") {
        const currentState = await isEnabled();
        console.log(`Auto-store status: ${currentState ? '✅ ENABLED' : '❌ DISABLED'}`);
      }
    },
  };
};
