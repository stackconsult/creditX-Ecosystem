"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";

interface A2UIComponent {
  type: string;
  id?: string;
  content?: string;
  elements?: A2UIComponent[];
  container?: any;
  label?: any;
  element?: any;
  value?: any;
  min?: number;
  max?: number;
  step?: number;
  options?: string[];
  selected?: string;
  controls?: any;
  url?: string;
  caption?: string;
  title?: string;
}

interface A2UIRendererProps {
  component: A2UIComponent;
  onAction?: (action: string, data: any) => void;
  className?: string;
}

const A2UIRenderer: React.FC<A2UIRendererProps> = ({ 
  component, 
  onAction,
  className = "" 
}) => {
  const renderComponent = (comp: A2UIComponent): React.ReactNode => {
    const { type, id, content, elements, ...props } = comp;

    switch (type) {
      case "Button":
        return (
          <Button
            id={id}
            className={`${className} ${props.element?.className || ""}`}
            onClick={() => onAction?.("click", { id, ...props })}
          >
            {content}
          </Button>
        );

      case "TextField":
        return (
          <div className={`space-y-2 ${props.container?.className || ""}`}>
            {props.label?.text && (
              <Label htmlFor={id}>{props.label.text}</Label>
            )}
            <Input
              id={id}
              placeholder={props.element?.placeholder}
              className={props.element?.className || ""}
              onChange={(e) => onAction?.("change", { id, value: e.target.value })}
            />
          </div>
        );

      case "Textarea":
        return (
          <div className={`space-y-2 ${props.container?.className || ""}`}>
            {props.label?.text && (
              <Label htmlFor={id}>{props.label.text}</Label>
            )}
            <Textarea
              id={id}
              placeholder={props.element?.placeholder}
              className={props.element?.className || ""}
              rows={props.element?.rows || 4}
              onChange={(e) => onAction?.("change", { id, value: e.target.value })}
            />
          </div>
        );

      case "Card":
        return (
          <Card className={props.container?.className || ""}>
            {props.title && (
              <CardHeader>
                <CardTitle>{props.title}</CardTitle>
              </CardHeader>
            )}
            <CardContent>
              {elements?.map((el, idx) => (
                <div key={idx} className="mb-4">
                  {renderComponent(el)}
                </div>
              ))}
            </CardContent>
          </Card>
        );

      case "Row":
        return (
          <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 ${props.container?.className || ""}`}>
            {elements?.map((el, idx) => (
              <div key={idx}>{renderComponent(el)}</div>
            ))}
          </div>
        );

      case "Column":
        return (
          <div className={`space-y-4 ${props.container?.className || ""}`}>
            {elements?.map((el, idx) => (
              <div key={idx}>{renderComponent(el)}</div>
            ))}
          </div>
        );

      case "Text":
        return (
          <p className={`${props.element?.className || ""} ${props.container?.className || ""}`}>
            {content}
          </p>
        );

      case "Heading":
        const HeadingTag = (props.level || 1) as keyof JSX.IntrinsicElements;
        return (
          <HeadingTag className={`${props.element?.className || ""} ${props.container?.className || ""}`}>
            {content}
          </HeadingTag>
        );

      case "Badge":
        return (
          <Badge variant={props.variant || "default"} className={props.element?.className || ""}>
            {content}
          </Badge>
        );

      case "Slider":
        return (
          <div className={`space-y-2 ${props.container?.className || ""}`}>
            {props.label?.text && (
              <Label>{props.label.text}</Label>
            )}
            <Slider
              value={[props.value || 0]}
              min={props.min || 0}
              max={props.max || 100}
              step={props.step || 1}
              onValueChange={(value) => onAction?.("change", { id, value: value[0] })}
              className={props.element?.className || ""}
            />
          </div>
        );

      case "Tabs":
        return (
          <Tabs className={props.container?.className || ""}>
            {props.controls?.tabs && (
              <TabsList>
                {props.controls.tabs.map((tab: any, idx: number) => (
                  <TabsTrigger key={idx} value={tab.id}>
                    {tab.label}
                  </TabsTrigger>
                ))}
              </TabsList>
            )}
            {elements?.map((el, idx) => (
              <TabsContent key={idx} value={el.id}>
                {renderComponent(el)}
              </TabsContent>
            ))}
          </Tabs>
        );

      case "Video":
        return (
          <div className={`aspect-video ${props.element?.className || ""}`}>
            <video
              controls
              className="w-full h-full rounded-lg"
              src={props.url}
            >
              Your browser does not support the video tag.
            </video>
          </div>
        );

      case "List":
        return (
          <ul className={`list-disc pl-6 space-y-1 ${props.container?.className || ""}`}>
            {elements?.map((el, idx) => (
              <li key={idx}>{renderComponent(el)}</li>
            ))}
          </ul>
        );

      case "MultipleChoice":
        return (
          <div className={`space-y-2 ${props.container?.className || ""}`}>
            {props.label?.text && (
              <Label>{props.label.text}</Label>
            )}
            {props.options?.map((option: string, idx: number) => (
              <div key={idx} className="flex items-center space-x-2">
                <input
                  type="radio"
                  id={`${id}-${idx}`}
                  name={id}
                  value={option}
                  checked={props.selected === option}
                  onChange={(e) => onAction?.("change", { id, value: e.target.value })}
                  className={props.element?.className || ""}
                />
                <Label htmlFor={`${id}-${idx}`}>{option}</Label>
              </div>
            ))}
          </div>
        );

      default:
        return (
          <div className="p-4 border border-dashed border-gray-300 rounded">
            <p className="text-sm text-gray-500">Unknown component type: {type}</p>
            <pre className="text-xs mt-2">{JSON.stringify(comp, null, 2)}</pre>
          </div>
        );
    }
  };

  return renderComponent(component);
};

export default A2UIRenderer;
