#!/usr/bin/env python3
"""
BPMN File Loader, Validator and Visualizer
This script loads, validates BPMN 2.0 XML files and generates visual diagrams
"""

import xml.etree.ElementTree as ET
import os
import sys
from pathlib import Path

# BPMN 2.0 namespaces
NAMESPACES = {
    'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
    'bpmn2': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
    'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
    'dc': 'http://www.omg.org/spec/DD/20100524/DC',
    'di': 'http://www.omg.org/spec/DD/20100524/DI',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}

class BPMNLoader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.tree = None
        self.root = None
        self.processes = []
        self.elements = {
            'tasks': [],
            'events': [],
            'gateways': [],
            'flows': []
        }
        
    def load(self):
        """Load and parse the BPMN file"""
        try:
            print(f"Loading BPMN file: {self.filepath}")
            self.tree = ET.parse(self.filepath)
            self.root = self.tree.getroot()
            
            # Detect namespace
            self.detect_namespace()
            
            print(f"[OK] File loaded successfully")
            print(f"  Root element: {self.root.tag}")
            
            return True
            
        except ET.ParseError as e:
            print(f"X XML Parse Error: {e}")
            return False
        except FileNotFoundError:
            print(f"X File not found: {self.filepath}")
            return False
        except Exception as e:
            print(f"X Error loading file: {e}")
            return False
    
    def detect_namespace(self):
        """Detect and set the correct namespace"""
        # Get namespace from root element
        if self.root.tag.startswith('{'):
            self.namespace = self.root.tag.split('}')[0][1:]
            print(f"  Detected namespace: {self.namespace}")
        else:
            self.namespace = None
            print("  No namespace detected")
    
    def validate_structure(self):
        """Validate basic BPMN structure"""
        print("\nValidating BPMN structure...")
        
        issues = []
        
        # Check for processes
        processes = self.find_elements('process')
        if not processes:
            issues.append("No process elements found")
        else:
            print(f"[OK] Found {len(processes)} process(es)")
            for process in processes:
                process_id = process.get('id', 'unnamed')
                process_name = process.get('name', 'unnamed')
                print(f"  - Process '{process_id}': {process_name}")
                self.processes.append({'id': process_id, 'name': process_name, 'element': process})
        
        # Check for start events
        start_events = self.find_elements('startEvent')
        if not start_events:
            issues.append("No start events found")
        else:
            print(f"[OK] Found {len(start_events)} start event(s)")
            for event in start_events:
                event_id = event.get('id', 'unnamed')
                event_name = event.get('name', 'no name')
                print(f"  - Start Event '{event_id}': {event_name}")
        
        # Check for end events
        end_events = self.find_elements('endEvent')
        if not end_events:
            issues.append("No end events found")
        else:
            print(f"[OK] Found {len(end_events)} end event(s)")
        
        # Check for tasks
        tasks = self.find_elements('task')
        if tasks:
            print(f"[OK] Found {len(tasks)} task(s)")
            for task in tasks[:5]:  # Show first 5 tasks
                task_id = task.get('id', 'unnamed')
                task_name = task.get('name', 'no name')
                print(f"  - Task '{task_id}': {task_name}")
            if len(tasks) > 5:
                print(f"  ... and {len(tasks) - 5} more")
        
        # Check for gateways
        gateways = []
        for gateway_type in ['exclusiveGateway', 'parallelGateway', 'inclusiveGateway', 'eventBasedGateway']:
            gateways.extend(self.find_elements(gateway_type))
        if gateways:
            print(f"[OK] Found {len(gateways)} gateway(s)")
        
        # Check for sequence flows
        flows = self.find_elements('sequenceFlow')
        if not flows:
            issues.append("No sequence flows found")
        else:
            print(f"[OK] Found {len(flows)} sequence flow(s)")
        
        # Check flow connectivity
        print("\nChecking flow connectivity...")
        self.check_connectivity(flows)
        
        # Report issues
        if issues:
            print("\n[WARNING] Validation Issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n[OK] Basic BPMN structure is valid")
        
        return len(issues) == 0
    
    def find_elements(self, element_type):
        """Find all elements of a specific type"""
        elements = []
        
        # Try with different namespace prefixes
        for prefix in ['bpmn2', 'bpmn', '']:
            if prefix:
                if self.namespace:
                    xpath = f".//{{{self.namespace}}}{element_type}"
                else:
                    xpath = f".//{prefix}:{element_type}"
            else:
                xpath = f".//{element_type}"
            
            try:
                found = self.root.findall(xpath, NAMESPACES)
                if found:
                    elements.extend(found)
                    break
            except:
                # Try without namespace
                found = self.root.findall(f".//{element_type}")
                if found:
                    elements.extend(found)
                    break
        
        return elements
    
    def check_connectivity(self, flows):
        """Check if all flows are properly connected"""
        disconnected = []
        
        # Get all element IDs
        all_elements = set()
        for element_type in ['task', 'startEvent', 'endEvent', 'exclusiveGateway', 
                            'parallelGateway', 'inclusiveGateway', 'eventBasedGateway',
                            'intermediateCatchEvent', 'intermediateThrowEvent']:
            elements = self.find_elements(element_type)
            for elem in elements:
                elem_id = elem.get('id')
                if elem_id:
                    all_elements.add(elem_id)
        
        # Check each flow
        for flow in flows:
            source = flow.get('sourceRef')
            target = flow.get('targetRef')
            flow_id = flow.get('id', 'unnamed')
            
            if source and source not in all_elements:
                disconnected.append(f"Flow '{flow_id}': source '{source}' not found")
            if target and target not in all_elements:
                disconnected.append(f"Flow '{flow_id}': target '{target}' not found")
        
        if disconnected:
            print(f"[WARNING] Found {len(disconnected)} disconnected flow(s):")
            for disc in disconnected[:5]:  # Show first 5
                print(f"  - {disc}")
            if len(disconnected) > 5:
                print(f"  ... and {len(disconnected) - 5} more")
        else:
            print("[OK] All flows are properly connected")
        
        return len(disconnected) == 0
    
    def extract_process_info(self):
        """Extract detailed information about the process"""
        print("\nExtracting process details...")
        
        for process_info in self.processes:
            process = process_info['element']
            print(f"\nProcess: {process_info['name']} (ID: {process_info['id']})")
            
            # Count elements in this process
            tasks = process.findall('.//bpmn2:task', NAMESPACES) or process.findall('.//task')
            events = (process.findall('.//bpmn2:startEvent', NAMESPACES) or process.findall('.//startEvent')) + \
                    (process.findall('.//bpmn2:endEvent', NAMESPACES) or process.findall('.//endEvent'))
            gateways = (process.findall('.//bpmn2:exclusiveGateway', NAMESPACES) or process.findall('.//exclusiveGateway'))
            flows = process.findall('.//bpmn2:sequenceFlow', NAMESPACES) or process.findall('.//sequenceFlow')
            
            print(f"  - Tasks: {len(tasks)}")
            print(f"  - Events: {len(events)}")
            print(f"  - Gateways: {len(gateways)}")
            print(f"  - Flows: {len(flows)}")
            
            # Show task names
            if tasks:
                print(f"  Task names:")
                for task in tasks[:10]:  # Show first 10
                    task_name = task.get('name', 'unnamed')
                    print(f"    - {task_name}")
                if len(tasks) > 10:
                    print(f"    ... and {len(tasks) - 10} more")
    
    def generate_diagram(self):
        """Generate a visual diagram of the BPMN process"""
        print("\n" + "="*50)
        print("Generating BPMN diagram...")
        
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            from matplotlib.patches import FancyBboxPatch, Circle, Polygon
            import networkx as nx
        except ImportError:
            print("[WARNING] matplotlib and/or networkx not installed.")
            print("Install with: pip install matplotlib networkx")
            return False
        
        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=(20, 12))
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 60)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Title
        plt.title('Source to Pay Process - BPMN Diagram', fontsize=16, fontweight='bold', pad=20)
        
        # Collect all elements
        elements_to_draw = []
        
        # Get elements for the first process
        if self.processes:
            process = self.processes[0]['element']
            
            # Collect tasks
            tasks = self.find_elements('task')
            for i, task in enumerate(tasks):
                task_id = task.get('id', f'task_{i}')
                task_name = task.get('name', 'Task')
                elements_to_draw.append({
                    'type': 'task',
                    'id': task_id,
                    'name': task_name,
                    'element': task
                })
            
            # Collect start events
            start_events = self.find_elements('startEvent')
            for i, event in enumerate(start_events):
                event_id = event.get('id', f'start_{i}')
                event_name = event.get('name', 'Start')
                elements_to_draw.append({
                    'type': 'startEvent',
                    'id': event_id,
                    'name': event_name,
                    'element': event
                })
            
            # Collect end events
            end_events = self.find_elements('endEvent')
            for i, event in enumerate(end_events):
                event_id = event.get('id', f'end_{i}')
                event_name = event.get('name', 'End')
                elements_to_draw.append({
                    'type': 'endEvent',
                    'id': event_id,
                    'name': event_name,
                    'element': event
                })
            
            # Collect gateways
            for gateway_type in ['exclusiveGateway', 'parallelGateway', 'inclusiveGateway']:
                gateways = self.find_elements(gateway_type)
                for i, gateway in enumerate(gateways):
                    gateway_id = gateway.get('id', f'gateway_{i}')
                    gateway_name = gateway.get('name', '')
                    elements_to_draw.append({
                        'type': gateway_type,
                        'id': gateway_id,
                        'name': gateway_name,
                        'element': gateway
                    })
        
        # Create a directed graph for layout
        G = nx.DiGraph()
        
        # Add nodes
        for elem in elements_to_draw:
            G.add_node(elem['id'], label=elem['name'], type=elem['type'])
        
        # Add edges from sequence flows
        flows = self.find_elements('sequenceFlow')
        for flow in flows:
            source = flow.get('sourceRef')
            target = flow.get('targetRef')
            if source in G.nodes() and target in G.nodes():
                G.add_edge(source, target)
        
        # Calculate layout using hierarchical layout
        try:
            # Try to create a hierarchical layout
            pos = self._hierarchical_layout(G, elements_to_draw)
        except:
            # Fallback to spring layout
            pos = nx.spring_layout(G, k=5, iterations=50, scale=80, center=[50, 30])
        
        # Draw elements
        for elem in elements_to_draw:
            elem_id = elem['id']
            if elem_id not in pos:
                continue
                
            x, y = pos[elem_id]
            elem_type = elem['type']
            name = elem['name']
            
            # Draw based on type
            if elem_type == 'task':
                # Draw task rectangle
                rect = FancyBboxPatch((x-4, y-2), 8, 4,
                                     boxstyle="round,pad=0.1",
                                     linewidth=1.5, edgecolor='black',
                                     facecolor='lightblue')
                ax.add_patch(rect)
                # Add text
                ax.text(x, y, self._wrap_text(name, 12), ha='center', va='center',
                       fontsize=8, fontweight='normal')
                
            elif elem_type == 'startEvent':
                # Draw start event circle
                circle = Circle((x, y), 1.5, linewidth=2, 
                              edgecolor='green', facecolor='lightgreen')
                ax.add_patch(circle)
                ax.text(x, y-3, name, ha='center', va='top', fontsize=7)
                
            elif elem_type == 'endEvent':
                # Draw end event circle
                circle = Circle((x, y), 1.5, linewidth=3, 
                              edgecolor='red', facecolor='lightcoral')
                ax.add_patch(circle)
                ax.text(x, y-3, name, ha='center', va='top', fontsize=7)
                
            elif 'Gateway' in elem_type:
                # Draw gateway diamond
                diamond = Polygon([(x, y+2), (x+2, y), (x, y-2), (x-2, y)],
                                closed=True, linewidth=1.5,
                                edgecolor='black', facecolor='yellow')
                ax.add_patch(diamond)
                if elem_type == 'exclusiveGateway':
                    # Add X for exclusive gateway
                    ax.plot([x-1, x+1], [y-1, y+1], 'k-', linewidth=1.5)
                    ax.plot([x-1, x+1], [y+1, y-1], 'k-', linewidth=1.5)
                if name:
                    ax.text(x, y-3, self._wrap_text(name, 10), ha='center', va='top', fontsize=7)
        
        # Draw sequence flows
        for flow in flows:
            source = flow.get('sourceRef')
            target = flow.get('targetRef')
            if source in pos and target in pos:
                x1, y1 = pos[source]
                x2, y2 = pos[target]
                
                # Draw arrow
                ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                          arrowprops=dict(arrowstyle='->', lw=1, color='black'))
                
                # Add flow name if exists
                flow_name = flow.get('name', '')
                if flow_name:
                    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                    ax.text(mid_x, mid_y, flow_name, ha='center', va='bottom',
                           fontsize=6, style='italic')
        
        # Save the figure
        output_file = os.path.splitext(self.filepath)[0] + '.jpg'
        plt.savefig(output_file, dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        print(f"[OK] Diagram saved to: {output_file}")
        
        # Show the plot (optional)
        # plt.show()
        plt.close()
        
        return True
    
    def _hierarchical_layout(self, G, elements):
        """Create a hierarchical layout for the graph"""
        pos = {}
        
        # Group elements by type
        start_events = [e for e in elements if e['type'] == 'startEvent']
        end_events = [e for e in elements if e['type'] == 'endEvent']
        tasks = [e for e in elements if e['type'] == 'task']
        gateways = [e for e in elements if 'Gateway' in e['type']]
        
        # Simple grid layout
        x_spacing = 10
        y_spacing = 8
        current_x = 5
        current_y = 30
        
        # Place start events
        for i, event in enumerate(start_events):
            pos[event['id']] = (current_x, current_y)
            current_x += x_spacing
        
        # Place tasks and gateways in layers
        all_middle = tasks + gateways
        # Sort by connectivity (nodes with more connections go in the middle)
        all_middle.sort(key=lambda e: G.degree(e['id']), reverse=True)
        
        # Layout in rows
        items_per_row = 5
        row = 0
        col = 0
        
        for elem in all_middle:
            x = 15 + col * x_spacing
            y = current_y - row * y_spacing
            pos[elem['id']] = (x, y)
            
            col += 1
            if col >= items_per_row:
                col = 0
                row += 1
        
        # Place end events
        current_x = 85
        for i, event in enumerate(end_events):
            pos[event['id']] = (current_x, current_y)
            current_x += x_spacing
        
        return pos
    
    def _wrap_text(self, text, max_length):
        """Wrap text to fit in shape"""
        if len(text) <= max_length:
            return text
        
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_length:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)

def main():
    # Get the BPMN file path
    bpmn_file = "source_to_pay_process.bpmn"
    
    # Check if file path was provided as argument
    if len(sys.argv) > 1:
        bpmn_file = sys.argv[1]
    
    # Convert to absolute path if relative
    if not os.path.isabs(bpmn_file):
        bpmn_file = os.path.join(os.path.dirname(__file__), bpmn_file)
    
    # Create loader instance
    loader = BPMNLoader(bpmn_file)
    
    # Load the file
    if loader.load():
        # Validate structure
        is_valid = loader.validate_structure()
        
        # Extract process information
        loader.extract_process_info()
        
        # Generate diagram
        loader.generate_diagram()
        
        print("\n" + "="*50)
        if is_valid:
            print("[OK] BPMN file is valid and can be loaded")
        else:
            print("[WARNING] BPMN file has validation issues")
            print("The file may not load correctly in BPMN viewers")
    else:
        print("\nX Failed to load BPMN file")
        sys.exit(1)

if __name__ == "__main__":
    main()