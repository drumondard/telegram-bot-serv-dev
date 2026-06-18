from rede_ftth import processar_consulta_rede
from fotos_bucket_equip import upload_para_bucket

async def handle_photo_router(update, context):
    servico = context.user_data.get('servico_ativo')
    if servico == 'UPLOAD_FOTO':
        await upload_para_bucket(update, context)
    # ...