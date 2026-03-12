"""
Neural Collaborative Filtering (NCF) model using PyTorch.
"""
import torch
import torch.nn as nn


class NCF(nn.Module):
    """
    Neural Collaborative Filtering: combines GMF and MLP pathways.
    """
    def __init__(self, num_users: int, num_items: int, emb_dim: int = 32, mlp_layers: list = None):
        super(NCF, self).__init__()
        if mlp_layers is None:
            mlp_layers = [64, 32, 16]
        
        # GMF embeddings
        self.gmf_user_emb = nn.Embedding(num_users, emb_dim)
        self.gmf_item_emb = nn.Embedding(num_items, emb_dim)
        
        # MLP embeddings
        self.mlp_user_emb = nn.Embedding(num_users, emb_dim)
        self.mlp_item_emb = nn.Embedding(num_items, emb_dim)
        
        # MLP layers
        mlp_input_size = emb_dim * 2
        layers = []
        for layer_size in mlp_layers:
            layers.append(nn.Linear(mlp_input_size, layer_size))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.2))
            mlp_input_size = layer_size
        self.mlp = nn.Sequential(*layers)
        
        # Final output
        self.output = nn.Linear(emb_dim + mlp_layers[-1], 1)
        self.sigmoid = nn.Sigmoid()
        
        self._init_weights()
    
    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Embedding):
                nn.init.normal_(m.weight, std=0.01)
            elif isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
    
    def forward(self, user_ids, item_ids):
        # GMF pathway
        gmf_u = self.gmf_user_emb(user_ids)
        gmf_i = self.gmf_item_emb(item_ids)
        gmf_out = gmf_u * gmf_i
        
        # MLP pathway
        mlp_u = self.mlp_user_emb(user_ids)
        mlp_i = self.mlp_item_emb(item_ids)
        mlp_in = torch.cat([mlp_u, mlp_i], dim=1)
        mlp_out = self.mlp(mlp_in)
        
        # Fusion
        concat = torch.cat([gmf_out, mlp_out], dim=1)
        output = self.sigmoid(self.output(concat))
        return output.squeeze()
