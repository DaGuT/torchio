"""
Tracing applied transforms
==========================

Sometimes we would like to see which transform was applied to a certain batch
during training. This can be done in TorchIO using
:func:`torchio.utils.history_collate` for the data loader. The transforms
history can be saved during training to check what was applied.
"""

import pprint
import torch
import torchio as tio
import matplotlib.pyplot as plt

torch.manual_seed(0)

batch_size = 4
subject = tio.datasets.FPG()
subject.remove_image('seg')
subjects = 4 * [subject]

transform = tio.Compose((
    tio.ToCanonical(),
    tio.RandomGamma(p=0.75),
    tio.RandomBlur(p=0.5),
    tio.RandomFlip(),
    tio.RescaleIntensity((-1, 1)),
))

dataset = tio.SubjectsDataset(subjects, transform=transform)

transformed = dataset[0]
print('Applied transforms:')  # noqa: T001
pprint.pprint(transformed.history)  # noqa: T003
print('\nComposed transform to reproduce history:')  # noqa: T001
print(transformed.get_composed_history())  # noqa: T001
print('\nComposed transform to invert applied transforms when possible:')  # noqa: T001, E501
print(transformed.get_inverse_transform(ignore_intensity=False))  # noqa: T001

loader = torch.utils.data.DataLoader(
    dataset,
    batch_size=batch_size,
    collate_fn=tio.utils.history_collate,
)

batch = tio.utils.get_first_item(loader)
print('\nTransforms applied to subjects in batch:')  # noqa: T001
pprint.pprint(batch[tio.HISTORY])  # noqa: T003

for i in range(batch_size):
    tensor = batch['t1'][tio.DATA][i]
    affine = batch['t1'][tio.AFFINE][i]
    image = tio.ScalarImage(tensor=tensor, affine=affine)
    image.plot(show=False)
    history = batch[tio.HISTORY][i]
    title = ', '.join(t.name for t in history)
    plt.suptitle(title)
    plt.tight_layout()

plt.show()
