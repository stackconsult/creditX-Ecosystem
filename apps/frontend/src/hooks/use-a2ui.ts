"use client";

import { useState, useCallback } from "react";
import { useAgent } from "@copilotkit/react-core";

interface A2UIAction {
  action: string;
  data: any;
}

interface A2UIState {
  components: any[];
  values: Record<string, any>;
  errors: Record<string, string>;
}

export const useA2UI = (agentId?: string) => {
  const agent = useAgent({ agentId });
  const [state, setState] = useState<A2UIState>({
    components: [],
    values: {},
    errors: {}
  });

  const updateComponent = useCallback((component: any) => {
    setState(prev => ({
      ...prev,
      components: [...prev.components, component]
    }));
  }, []);

  const updateValue = useCallback((id: string, value: any) => {
    setState(prev => ({
      ...prev,
      values: {
        ...prev.values,
        [id]: value
      },
      errors: {
        ...prev.errors,
        [id]: undefined
      }
    }));
  }, []);

  const setError = useCallback((id: string, error: string) => {
    setState(prev => ({
      ...prev,
      errors: {
        ...prev.errors,
        [id]: error
      }
    }));
  }, []);

  const clearComponents = useCallback(() => {
    setState(prev => ({
      ...prev,
      components: []
    }));
  }, []);

  const handleSubmit = useCallback(async (componentId?: string) => {
    try {
      // Send form data to agent
      if (agent) {
        const formData = componentId 
          ? { [componentId]: state.values[componentId] }
          : state.values;

        await agent.addMessage({
          id: Date.now().toString(),
          role: "user",
          content: JSON.stringify(formData),
          timestamp: new Date().toISOString()
        });

        // Clear form after submission
        setState(prev => ({
          ...prev,
          values: {},
          errors: {}
        }));
      }
    } catch (error) {
      console.error("Failed to submit form:", error);
    }
  }, [agent, state.values]);

  const handleAction = useCallback(async (action: A2UIAction) => {
    const { action: actionType, data } = action;

    switch (actionType) {
      case "change":
        updateValue(data.id, data.value);
        break;
      
      case "click":
        // Handle button clicks
        if (data.id === "submit") {
          await handleSubmit();
        } else if (data.action) {
          // Execute custom action
          if (agent) {
            await agent.addMessage({
              id: Date.now().toString(),
              role: "user",
              content: JSON.stringify({
                action: data.action,
                data: data.data || {}
              }),
              timestamp: new Date().toISOString()
            });
          }
        }
        break;
      
      case "validate":
        // Validate field
        const validation = validateField(data.id, data.value, data.rules);
        if (!validation.isValid) {
          setError(data.id, validation.error);
        } else {
          setError(data.id, "");
        }
        break;
      
      default:
        console.log("Unknown action:", action);
    }
  }, [agent, updateValue, setError, handleSubmit]);

  // Listen for agent messages that contain A2UI components
  React.useEffect(() => {
    if (agent && agent.messages.length > 0) {
      const lastMessage = agent.messages[agent.messages.length - 1];
      
      // Check if message contains A2UI specification
      if (lastMessage.role === "assistant" && lastMessage.content) {
        try {
          const content = typeof lastMessage.content === "string" 
            ? JSON.parse(lastMessage.content)
            : lastMessage.content;

          if (content.a2ui || content.components) {
            const components = content.a2ui || content.components;
            if (Array.isArray(components)) {
              components.forEach(comp => updateComponent(comp));
            }
          }
        } catch (error) {
          // Not JSON, ignore
        }
      }
    }
  }, [agent?.messages, updateComponent]);

  return {
    state,
    updateComponent,
    updateValue,
    setError,
    clearComponents,
    handleAction,
    handleSubmit,
    agent
  };
};

// Validation helper
function validateField(fieldId: string, value: any, rules: any = {}) {
  if (rules.required && (!value || value.toString().trim() === "")) {
    return { isValid: false, error: "This field is required" };
  }

  if (rules.minLength && value.length < rules.minLength) {
    return { isValid: false, error: `Minimum length is ${rules.minLength}` };
  }

  if (rules.maxLength && value.length > rules.maxLength) {
    return { isValid: false, error: `Maximum length is ${rules.maxLength}` };
  }

  if (rules.pattern && !new RegExp(rules.pattern).test(value)) {
    return { isValid: false, error: "Invalid format" };
  }

  return { isValid: true, error: "" };
}
