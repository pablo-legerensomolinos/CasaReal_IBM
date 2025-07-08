from pymilvus import CollectionSchema, DataType, FieldSchema, MilvusClient

class QueriesSummSchema:
        collection_name = 'queries_summaries'

        id = FieldSchema(
            name="id", dtype=DataType.INT64,
            descrition="primary field", is_primary=True, auto_id=True)
        content_field = FieldSchema(
            name='content', dtype=DataType.STRING,
            description='Content of the full criteria that has been generated and published for different citizen queries')
        content_vector_sparse_field = FieldSchema(
            name='vector_sparse', dtype=DataType.SPARSE_FLOAT_VECTOR, description='Vector of the content field')
        content_vector_dense_field = FieldSchema(
            name='vector_dense', dtype=DataType.FLOAT_VECTOR, description='Vector of the content field')
        title_field = FieldSchema(
            name='title', dtype=DataType.STRING,
            description='Title of the published criteria, including the Query identifier')
        chunk_id_title_field = FieldSchema(
            name='chunk_id_title', dtype=DataType.INT32, description='Identifier of the chunk within the Section')
        chunk_id_field = FieldSchema(
            name='chunk_id', dtype=DataType.INT32,
            description='Identifier of the chunk within the document')
        doc_name_field = FieldSchema(
            name='doc_name', dtype=DataType.INT32,
            description='Name of the original document from where the content has been extracted')
        word_count_field = FieldSchema(
            name='word_count', dtype=DataType.INT32,
            description='Number of words that compose the content_field')
        references_in_section_field = FieldSchema(
            name='references_in_section', dtype=DataType.ARRAY, element_type=DataType.STRING,
            description='List of other sections within the document that have been referenced in this section')

        schema = CollectionSchema(
            fields=[
                id,
                content_field,
                content_vector_sparse_field,
                content_vector_dense_field,
                title_field,
                chunk_id_field,
                chunk_id_title_field,
                doc_name_field,
                word_count_field,
                references_in_section_field
            ],
            auto_id=False, enable_dynamic_field=True, description="desc of a collection")

        index_params = MilvusClient.prepare_index_params()
        index_params.add_index(
            field_name='id',
            index_type='STL_SORT'
        )
        index_params.add_index(
            field_name='vector_sparse',
            index_type='SPARSE_INVERTED_INDEX',
            metric_type='IP'
        )
        # TODO: @HUGO @ALICIA check this
        # https://milvus.io/docs/index-vector-fields.md?tab=floating
        index_params.add_index(
            field_name='vector_dense',
            index_type='HNSW',  # <<
            metric_type='COSINE'  # <<
        )
