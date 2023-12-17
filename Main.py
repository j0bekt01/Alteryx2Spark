import streamlit as st
import xml.etree.ElementTree as ET
from Node import NodeElement
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import io

def process_yxmd(file_content):
     tree = ET.fromstring(file_content)

     graph = nx.DiGraph()
     lst = []
     for x in tree.iter('Node'):
         node = NodeElement(x, tree)
         lst.append(node.data)
         graph.add_node(node.data['Tool ID'])
     mst=[]
     for node in nx.algorithms.topological_sort(graph):
        mst = mst + ([d for d in lst if int(d.get('Tool ID')) == int(node)])

     for connection in tree.find('Connections').findall('Connection'):
        origin_tool_id = connection.find('Origin').attrib['ToolID']
        destination_tool_id = connection.find('Destination').attrib['ToolID']
        graph.add_edge(origin_tool_id, destination_tool_id)
     processed_data = mst 
     return processed_data,graph

def main():
    st.title('Alteryx to Spark Converter')

    uploaded_file = st.file_uploader("Upload your alteryx .yxmd file", type="yxmd")

    if uploaded_file is not None:
        file_content = uploaded_file.getvalue()

        # Process the file when the user clicks the button
        if st.button('Process'):
            processed_data, graph = process_yxmd(file_content)
            st.write("Alteryx to Spark details")
            st.dataframe(pd.DataFrame(processed_data))  

            # code for dag image 
            pos = nx.spring_layout(nx.algorithms.topological_sort(graph), seed=142)
            for node_data in processed_data:
                tool_id = node_data['Tool ID']
                x = node_data.get('x')  
                y = node_data.get('y')
                if x is not None and y is not None:
                    pos[tool_id] = (int(x), int(y))
            plt.figure(figsize=(50, 30))
            nx.draw(graph, pos, with_labels=True, node_size=1000, node_color='skyblue', font_size=10, font_color='black', font_weight='bold', arrowsize=20)
            edge_labels = {(u, v): v for u, v in graph.edges}
            nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_color='red')
            plt.title("Directed Acyclic Graph (DAG)")
            img_bytes = io.BytesIO()
            plt.savefig(img_bytes, format='png', bbox_inches='tight')
            plt.close()
            st.write("DAG Image:")
            st.image(img_bytes, caption='Directed Acyclic Graph (DAG)')
            st.download_button(label='Download DAG Image', data=img_bytes, file_name='dag_image.png', mime='image/png')

if __name__ == '__main__':
    main()
